package dev.kutti.app.terminal

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import dev.kutti.app.databinding.ActivityTerminalBinding

class TerminalActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityTerminalBinding
    private var terminalSession: TerminalSession? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        binding = ActivityTerminalBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Set up terminal view
        setupTerminalView()
        
        // Set up toolbar
        setupToolbar()
    }
    
    private fun setupTerminalView() {
        terminalSession = TerminalSession(this) {
            // Session finished
            finish()
        }
        
        binding.terminalView.attachSession(terminalSession)
    }
    
    private fun setupToolbar() {
        binding.toolbar.setOnMenuItemClickListener { menuItem ->
            when (menuItem.itemId) {
                android.R.id.home -> {
                    onBackPressedDispatcher.onBackPressed()
                    true
                }
                else -> false
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        terminalSession?.close()
    }
}
