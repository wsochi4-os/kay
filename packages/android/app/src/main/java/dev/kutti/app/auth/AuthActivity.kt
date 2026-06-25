package dev.kutti.app.auth

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import dev.kutti.app.databinding.ActivityAuthBinding

class AuthActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityAuthBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        binding = ActivityAuthBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupWebView()
        setupToolbar()
    }
    
    private fun setupWebView() {
        // Load the auth web page
        // This would load a local HTML page or a remote auth page
        binding.webView.settings.javaScriptEnabled = true
        binding.webView.settings.domStorageEnabled = true
        
        // Load local auth page
        binding.webView.loadUrl("file:///android_asset/auth.html")
    }
    
    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener {
            onBackPressedDispatcher.onBackPressed()
        }
    }
}
