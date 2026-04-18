from config.logging_config import logger
from scraper.ai.providers.gemini import Gemini
from scraper.ai.providers.groq import Groq


class AIManager:
    """
    Manager untuk mengelola multiple AI providers dengan fallback logic.
    
    Fitur:
    - Automatic provider switching saat rate limit
    - Recursive fallback ke provider berikutnya
    - Logging untuk tracking provider usage
    - State management untuk track provider health
    """
    
    def __init__(self):
        """Initialize AI Manager dengan list provider yang tersedia."""
        self.providers = [
            Gemini(),
            Groq()
        ]
        self.current_provider_index = 0
        
        logger.info(f"🤖 AIManager initialized dengan {len(self.providers)} provider(s)")
    
    def _get_current_provider(self):
        """Get provider yang sedang aktif."""
        if self.current_provider_index >= len(self.providers):
            return None
        return self.providers[self.current_provider_index]
    
    def _get_provider_name(self, provider_index=None):
        """Get nama provider untuk logging."""
        if provider_index is None:
            provider_index = self.current_provider_index
        
        if provider_index >= len(self.providers):
            return "Unknown"
        
        return self.providers[provider_index].__class__.__name__
    
    def _switch_to_next_provider(self):
        """Switch ke provider berikutnya."""
        current_name = self._get_provider_name()
        self.current_provider_index += 1
        next_name = self._get_provider_name()
        
        logger.warning(
            f"⚠️ Provider '{current_name}' mencapai batas. "
            f"Switching ke '{next_name}'..."
        )
    
    def process(self, valid_tags, batch_lomba_mentah):
        """
        Main method untuk process batch menggunakan AI provider.
        
        Args:
            valid_tags (list): List tag yang valid untuk classification
            batch_lomba_mentah (list): Batch data lomba yang akan diproses
        
        Returns:
            list: Array JSON hasil proses, atau None jika semua provider gagal
        
        Note:
            Setiap provider sudah memiliki internal retry logic dengan model rotation.
            Jika provider return None, berarti semua model/attempt sudah habis.
            Tidak perlu retry provider yang sama lagi.
        """
        # Validasi input
        if not batch_lomba_mentah:
            logger.warning("⚠️ Batch kosong, tidak ada yang perlu diproses")
            return []
        
        if not valid_tags:
            logger.warning("⚠️ Valid tags kosong, proses mungkin tidak optimal")
        
        # Check apakah masih ada provider yang available
        if self.current_provider_index >= len(self.providers):
            logger.error("❌ Semua provider telah exhausted. Tidak bisa memproses batch.")
            return None
        
        current_provider = self._get_current_provider()
        provider_name = self._get_provider_name()
        
        logger.info(f"📤 Processing batch dengan provider: {provider_name}")
        
        try:
            # Panggil provider, sudah termasuk internal retry dengan model rotation
            result = current_provider.strukturkan_dengan_ai(valid_tags, batch_lomba_mentah)
            
            if result is not None:
                logger.info(f"✅ Batch berhasil diproses oleh '{provider_name}'")
                return result
            
            # Jika None, berarti provider sudah exhausted, switch ke berikutnya
            logger.warning(
                f"❌ Provider '{provider_name}' gagal memproses batch "
                f"(semua model/attempt sudah habis). Switching ke provider berikutnya..."
            )
            self._switch_to_next_provider()
            return self.process(valid_tags, batch_lomba_mentah)
            
        except Exception as e:
            logger.error(f"❌ Unexpected error di provider '{provider_name}': {e}")
            self._switch_to_next_provider()
            return self.process(valid_tags, batch_lomba_mentah)
    
    def get_provider_status(self):
        """Get status semua provider (untuk debugging)."""
        status = []
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__
            is_current = i == self.current_provider_index
            
            status.append({
                'name': provider_name,
                'is_current': is_current,
                'is_limit': provider.is_limit
            })
        
        return status