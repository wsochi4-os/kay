package dev.kutti.app.terminal

import android.content.Context
import android.os.Environment
import dev.kutti.app.ubuntu.ProotRunner
import java.io.File

class TerminalSession(
    private val context: Context,
    private val onFinished: () -> Unit
) {
    
    private val prootRunner: ProotRunner
    private val ubuntuRoot: File
    
    init {
        // Get Ubuntu root directory
        val filesDir = context.getDir("ubuntu", Context.MODE_PRIVATE)
        ubuntuRoot = File(filesDir, "rootfs")
        
        prootRunner = ProotRunner(context, ubuntuRoot)
    }
    
    fun getPty(): TerminalPty {
        return object : TerminalPty {
            override fun read(buffer: ByteArray, offset: Int, length: Int): Int {
                return prootRunner.read(buffer, offset, length)
            }
            
            override fun write(buffer: ByteArray, offset: Int, length: Int): Int {
                return prootRunner.write(buffer, offset, length)
            }
            
            override fun close() {
                prootRunner.close()
                onFinished()
            }
        }
    }
    
    fun close() {
        prootRunner.close()
    }
}

interface TerminalPty {
    fun read(buffer: ByteArray, offset: Int, length: Int): Int
    fun write(buffer: ByteArray, offset: Int, length: Int): Int
    fun close()
}
