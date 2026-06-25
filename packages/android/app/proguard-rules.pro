# Android ProGuard rules for Kutti
# Add project specific ProGuard rules here.
# By default, the flags in proguard-android-optimize.txt are used.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# Add any project specific keep options here:

# Keep all activities, services, and receivers
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver

# Keep all views
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}

# Keep R classes
-keep class **.R
-keep class **.R$* {
    <fields>;
}

# Keep Kotlin metadata
-keep class kotlin.Metadata { *; }
-keep class kotlin.** { *; }

# Keep coroutines
-keep class kotlinx.coroutines.** { *; }

# Keep Termux terminal classes
-keep class dev.termux.** { *; }

# Keep all classes in the dev.kutti package
-keep class dev.kutti.** { *; }
