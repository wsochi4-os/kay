package dev.kutti.app.auth

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys
import dev.kutti.app.KuttiApplication

class TokenStore private constructor(context: Context) {
    
    companion object {
        private const val PREFS_NAME = "kutti_auth"
        private const val KEY_API_KEY = "api_key_"
        private const val KEY_ACTIVE_PROVIDER = "active_provider"
        
        private var instance: TokenStore? = null
        
        fun getInstance(context: Context = KuttiApplication.appContext): TokenStore {
            if (instance == null) {
                instance = TokenStore(context)
            }
            return instance!!
        }
    }
    
    private val masterKeyAlias: String = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
    
    private val sharedPreferences: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        PREFS_NAME,
        masterKeyAlias,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    fun saveApiKey(provider: String, apiKey: String) {
        sharedPreferences.edit().putString(KEY_API_KEY + provider, apiKey).apply()
    }
    
    fun getApiKey(provider: String): String? {
        return sharedPreferences.getString(KEY_API_KEY + provider, null)
    }
    
    fun removeApiKey(provider: String) {
        sharedPreferences.edit().remove(KEY_API_KEY + provider).apply()
    }
    
    fun removeAllApiKeys() {
        val keys = sharedPreferences.all.keys.filter { it.startsWith(KEY_API_KEY) }
        val editor = sharedPreferences.edit()
        for (key in keys) {
            editor.remove(key)
        }
        editor.apply()
    }
    
    fun setActiveProvider(provider: String) {
        sharedPreferences.edit().putString(KEY_ACTIVE_PROVIDER, provider).apply()
    }
    
    fun getActiveProvider(): String? {
        return sharedPreferences.getString(KEY_ACTIVE_PROVIDER, null)
    }
    
    fun getAllProviders(): List<String> {
        return sharedPreferences.all.keys
            .filter { it.startsWith(KEY_API_KEY) }
            .map { it.removePrefix(KEY_API_KEY) }
    }
    
    fun isAuthenticated(provider: String): Boolean {
        return getApiKey(provider) != null
    }
}
