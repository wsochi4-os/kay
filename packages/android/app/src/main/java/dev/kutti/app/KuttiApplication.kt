package dev.kutti.app

import android.app.Application
import android.content.Context
import dev.kutti.app.ubuntu.UbuntuManager

class KuttiApplication : Application() {
    
    companion object {
        private lateinit var instance: KuttiApplication
        val appContext: Context get() = instance.applicationContext
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        
        // Initialize Ubuntu environment
        UbuntuManager.initialize(this)
    }
}
