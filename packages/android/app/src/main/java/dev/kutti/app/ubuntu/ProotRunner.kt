package dev.kutti.app.ubuntu

import android.content.Context
import android.util.Log
import java.io.File
import java.io.InputStream
import java.io.OutputStream

class ProotRunner(
    private val context: Context,
    private val rootfs: File
) {
    
    companion object {
        private const val TAG = "ProotRunner"
        private const val PROOT_BINARY = "proot"
    }
    
    private var process: Process? = null
    private var inputStream: InputStream? = null
    private var outputStream: OutputStream? = null
    private var errorStream: InputStream? = null
    
    init {
        // Copy proot binary to cache dir if needed
        ensureProotBinary()
    }
    
    private fun ensureProotBinary() {
        val prootFile = File(context.cacheDir, PROOT_BINARY)
        if (!prootFile.exists()) {
            try {
                val inputStream = context.assets.open(PROOT_BINARY)
                val outputStream = FileOutputStream(prootFile)
                
                inputStream.use { input ->
                    outputStream.use { output ->
                        input.copyTo(output)
                    }
                }
                
                prootFile.setExecutable(true)
                Log.i(TAG, "Proot binary copied")
            } catch (e: Exception) {
                Log.e(TAG, "Failed to copy proot binary", e)
            }
        }
    }
    
    fun execute(command: String): String {
        try {
            val prootFile = File(context.cacheDir, PROOT_BINARY)
            
            val builder = ProcessBuilder(
                prootFile.absolutePath,
                "--link2symlink",
                "-0",
                "-r", rootfs.absolutePath,
                "-b", "/dev",
                "-b", "/proc",
                "-b", "/sys",
                "/bin/sh",
                "-c", command
            )
            
            builder.directory(rootfs)
            builder.redirectErrorStream(true)
            
            process = builder.start()
            inputStream = process?.inputStream
            outputStream = process?.outputStream
            errorStream = process?.errorStream
            
            // Read output
            val output = inputStream?.bufferedReader()?.readText() ?: ""
            
            // Wait for process to finish
            val exitCode = process?.waitFor() ?: -1
            
            if (exitCode != 0) {
                Log.e(TAG, "Proot command failed with exit code: $exitCode")
            }
            
            return output
        } catch (e: Exception) {
            Log.e(TAG, "Failed to execute proot command", e)
            throw e
        }
    }
    
    fun read(buffer: ByteArray, offset: Int, length: Int): Int {
        return inputStream?.read(buffer, offset, length) ?: -1
    }
    
    fun write(buffer: ByteArray, offset: Int, length: Int): Int {
        return outputStream?.write(buffer, offset, length) ?: -1
    }
    
    fun close() {
        try {
            outputStream?.close()
            inputStream?.close()
            errorStream?.close()
            process?.destroy()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to close proot process", e)
        }
    }
}
