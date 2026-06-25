package dev.kutti.app

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import dev.kutti.app.ubuntu.UbuntuManager
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Check if Ubuntu is set up
        lifecycleScope.launch {
            val ubuntuManager = UbuntuManager.getInstance(this@MainActivity)
            
            if (ubuntuManager.isUbuntuInstalled()) {
                // Ubuntu is ready, launch terminal
                startTerminal()
            } else {
                // Need to set up Ubuntu
                ubuntuManager.setupUbuntu { success ->
                    if (success) {
                        startTerminal()
                    } else {
                        // Show error
                        finish()
                    }
                }
            }
        }
    }
    
    private fun startTerminal() {
        val intent = Intent(this, dev.kutti.app.terminal.TerminalActivity::class.java)
        startActivity(intent)
        finish()
    }
}
