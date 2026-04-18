import os
import json
import time
from google import genai
from google.genai import types
from config.logging_config import logger
from scraper.ai.providers.base import BaseAIProvider


class Gemini(BaseAIProvider):
    """
    Gemini AI Provider untuk processing batch data.
    
    Fitur:
    - Multiple model fallback (flash, pro)
    - Exponential backoff retry logic
    - Rate limit detection dan handling
    - Robust JSON parsing
    - Efficient client management
    """
    
    @property
    def model_list(self):
        """List model Gemini yang tersedia untuk fallback."""
        return [
            # --- Pilihan Utama (Cepat dan Cukup Cerdas) ---
            'models/gemini-flash-latest',
            'models/gemini-2.5-flash',
            
            # --- Pilihan Kedua (Lebih Cerdas, Mungkin Sedikit Lebih Lambat) ---
            'models/gemini-pro-latest',
            'models/gemini-2.5-pro',
        ]

    def __init__(self):
        """Initialize Gemini provider."""
        super().__init__()
        self.current_model_index = 0
        self._client = None  # Cache client untuk reuse

    def _get_client(self):
        """
        Get atau create Gemini client (lazy initialization).
        
        Returns:
            genai.Client: Gemini API client
        """
        if self._client is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable tidak ditemukan")
            self._client = genai.Client(api_key=api_key)
        return self._client

    def _is_rate_limit_error(self, error_str):
        """
        Check apakah error adalah rate limit error.
        
        Args:
            error_str (str): Error message string
        
        Returns:
            bool: True jika rate limit error
        """
        rate_limit_indicators = ["429", "RESOURCE_EXHAUSTED", "503", "quota", "rate limit"]
        error_lower = str(error_str).lower()
        return any(indicator in error_lower for indicator in rate_limit_indicators)

    def _parse_json_response(self, response_text):
        """
        Parse JSON response dari AI dengan validation.
        
        Args:
            response_text (str): Raw response text dari AI
        
        Returns:
            list: Parsed JSON array, atau None jika parsing gagal
        
        Raises:
            ValueError: Jika response tidak valid JSON
        """
        try:
            data = json.loads(response_text)
            
            # Validate struktur response
            if not isinstance(data, list):
                raise ValueError(f"Response harus array, tapi diterima {type(data).__name__}")
            
            if len(data) == 0:
                logger.warning("⚠️ Response array kosong")
                return []
            
            # Minimal validation: check first item punya minimal field
            first_item = data[0]
            if not isinstance(first_item, dict):
                raise ValueError(f"Array item harus object, tapi diterima {type(first_item).__name__}")
            
            if "title" not in first_item or "source_url" not in first_item:
                raise ValueError("Response item kehilangan field wajib (title/source_url)")
            
            logger.info(f"✅ JSON response valid: {len(data)} item(s) berhasil diparse")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing gagal: {e}")
            logger.error(f"Response text (first 200 chars): {response_text[:200]}")
            raise ValueError(f"Invalid JSON response: {e}")
        except ValueError as e:
            logger.error(f"❌ Response validation gagal: {e}")
            raise

    def _switch_to_next_model(self):
        """Switch ke model berikutnya dan set is_limit flag."""
        current_model = self.model_list[self.current_model_index]
        self.current_model_index += 1
        
        if self.current_model_index >= len(self.model_list):
            logger.error("❌ Semua model sudah exhausted. Setting is_limit = True")
            self.is_limit = True
            next_model = "NONE (exhausted)"
        else:
            next_model = self.model_list[self.current_model_index]
        
        logger.warning(
            f"⚠️ Model '{current_model}' gagal. "
            f"Switching ke '{next_model}'..."
        )

    def strukturkan_dengan_ai(self, valid_tags, batch_lomba_mentah):
        """
        Main method untuk process batch data dengan Gemini API.
        
        Args:
            valid_tags (list): List tag yang valid untuk classification
            batch_lomba_mentah (list): Batch data lomba yang akan diproses
        
        Returns:
            list: Array JSON hasil proses, atau None jika semua model gagal
        """
        logger.info("\n--- Menghubungi Gemini AI untuk menstrukturkan data... ---")
        
        # Check apakah sudah exhausted
        if self.current_model_index >= len(self.model_list):
            logger.error("❌ Semua model telah exhausted. Tidak bisa memproses batch.")
            self.is_limit = True
            return None
        
        current_model_name = self.model_list[self.current_model_index]
        logger.info(f"📝 Menggunakan model: {current_model_name}")
        
        # Generate prompt sekali untuk semua attempt
        try:
            prompt = self.get_batch_prompt(valid_tags, batch_lomba_mentah)
        except ValueError as e:
            logger.error(f"❌ Error saat generate prompt: {e}")
            return None
        
        # Retry logic per model
        total_attempt = self.MAX_RETRIES_PER_MODEL
        for attempt in range(total_attempt):
            try:
                # Get client (reuse atau create baru)
                client = self._get_client()
                
                logger.info(
                    f"🔄 Attempt {attempt + 1}/{total_attempt} dengan model '{current_model_name}'..."
                )
                
                # Call API
                response = client.models.generate_content(
                    model=current_model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json'
                    )
                )
                
                # Parse dan validate response
                batch_data_terstruktur = self._parse_json_response(response.text)
                
                logger.info(
                    f"✅ Batch berhasil diproses dengan model '{current_model_name}'. "
                    f"Total {len(batch_data_terstruktur)} item(s) processed."
                )
                return batch_data_terstruktur
                
            except Exception as e:
                error_str = str(e)
                is_rate_limit = self._is_rate_limit_error(error_str)
                
                if is_rate_limit:
                    if attempt < total_attempt - 1:
                        # Bukan attempt terakhir, tunggu dan retry
                        wait_time = self.BASE_DELAY * (2 ** attempt)
                        logger.warning(
                            f"⚠️ Rate limit error. Menunggu {wait_time}s... "
                            f"(Attempt {attempt + 1}/{total_attempt})"
                        )
                        time.sleep(wait_time)
                    else:
                        # Attempt terakhir, switch ke model berikutnya
                        logger.warning(
                            f"⚠️ Rate limit pada attempt terakhir model '{current_model_name}'. "
                            f"Semua {total_attempt} attempt sudah habis."
                        )
                        self._switch_to_next_model()
                        # Recursive call dengan parameter lengkap
                        return self.strukturkan_dengan_ai(valid_tags, batch_lomba_mentah)
                else:
                    # Error tidak terduga (bukan rate limit)
                    logger.error(
                        f"❌ Error tidak terduga di model '{current_model_name}': {e}"
                    )
                    return None
        
        # Jika semua attempt habis tanpa return (shouldn't reach here)
        logger.error(f"❌ Semua {total_attempt} attempt gagal untuk model '{current_model_name}'")
        return None