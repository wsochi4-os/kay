package dev.kutti.app.ubuntu

import android.content.Context
import android.os.Environment
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

class UbuntuManager private constructor(private val context: Context) {
    
    companion object {
        private const val TAG = "UbuntuManager"
        private const val UBUNTU_DIR = "ubuntu"
        private const val ROOTFS_FILE = "bootstrap-aarch64.tar.gz"
        private const val BOOTSTRAP_SCRIPT = "kutti-bootstrap.sh"
        
        private var instance: UbuntuManager? = null
        
        fun initialize(context: Context) {
            if (instance == null) {
                instance = UbuntuManager(context.applicationContext)
            }
        }
        
        fun getInstance(context: Context): UbuntuManager {
            if (instance == null) {
                initialize(context)
            }
            return instance!!
        }
    }
    
    private val ubuntuDir: File by lazy {
        File(context.getDir(UBUNTU_DIR, Context.MODE_PRIVATE).absolutePath)
    }
    
    private val rootfsFile: File by lazy {
        File(ubuntuDir, ROOTFS_FILE)
    }
    
    private val rootfsDir: File by lazy {
        File(ubuntuDir, "rootfs")
    }
    
    fun isUbuntuInstalled(): Boolean {
        return rootfsDir.exists() && 
               File(rootfsDir, "bin/bash").exists() &&
               File(rootfsDir, "home/kutti").exists()
    }
    
    suspend fun setupUbuntu(callback: (Boolean) -> Unit) {
        withContext(Dispatchers.IO) {
            try {
                // Check if already installed
                if (isUbuntuInstalled()) {
                    callback(true)
                    return@withContext
                }
                
                // Create directories
                ubuntuDir.mkdirs()
                
                // Extract bootstrap if needed
                if (!rootfsFile.exists()) {
                    extractBootstrap()
                }
                
                // Extract rootfs
                extractRootfs()
                
                // Run bootstrap script
                runBootstrap()
                
                callback(true)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to setup Ubuntu", e)
                callback(false)
            }
        }
    }
    
    private fun extractBootstrap() {
        try {
            val inputStream = context.assets.open(ROOTFS_FILE)
            val outputStream = FileOutputStream(rootfsFile)
            
            inputStream.use { input ->
                outputStream.use { output ->
                    input.copyTo(output)
                }
            }
            
            Log.i(TAG, "Bootstrap extracted")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to extract bootstrap", e)
            throw e
        }
    }
    
    private fun extractRootfs() {
        try {
            // This would use tar to extract the rootfs
            // For now, we'll just create the directory structure
            rootfsDir.mkdirs()
            
            // Create basic directory structure
            File(rootfsDir, "bin").mkdirs()
            File(rootfsDir, "usr").mkdirs()
            File(rootfsDir, "lib").mkdirs()
            File(rootfsDir, "home/kutti").mkdirs()
            File(rootfsDir, "etc").mkdirs()
            File(rootfsDir, "var").mkdirs()
            
            Log.i(TAG, "Rootfs structure created")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to extract rootfs", e)
            throw e
        }
    }
    
    private fun runBootstrap() {
        try {
            // Copy bootstrap script to rootfs
            val bootstrapScript = File(rootfsDir, BOOTSTRAP_SCRIPT)
            val inputStream = context.assets.open(BOOTSTRAP_SCRIPT)
            
            inputStream.use { input ->
                FileOutputStream(bootstrapScript).use { output ->
                    input.copyTo(output)
                }
            }
            
            // Make executable
            bootstrapScript.setExecutable(true)
            
            // Run the bootstrap script via proot
            val prootRunner = ProotRunner(context, rootfsDir)
            prootRunner.execute("/kutti-bootstrap.sh")
            
            Log.i(TAG, "Bootstrap script executed")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to run bootstrap", e)
            throw e
        }
    }
    
    fun getUbuntuRoot(): File {
        return rootfsDir
    }
}
