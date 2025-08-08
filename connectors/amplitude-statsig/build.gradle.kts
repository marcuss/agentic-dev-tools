import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.dsl.KotlinVersion

plugins {
   kotlin("jvm")
}

subprojects {
   apply(plugin = "org.jetbrains.kotlin.jvm")

   dependencies {
      api(rootProject.libs.accelerator.kotlin)
      testImplementation(rootProject.libs.accelerator.testkit)
   }

   java {
      targetCompatibility = JavaVersion.VERSION_21
      sourceCompatibility = JavaVersion.VERSION_21
      withSourcesJar()
   }

   tasks.test {
      useJUnitPlatform()
      testLogging {
         showExceptions = true
         showStandardStreams = true
         exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
      }
   }

   kotlin {
      compilerOptions {
         languageVersion = KotlinVersion.KOTLIN_2_1
         apiVersion = KotlinVersion.KOTLIN_2_1
         jvmTarget = JvmTarget.JVM_21
      }
   }

   sourceSets {
      main {
         kotlin {
            setSrcDirs(listOf("src/main/kotlin", "src/main/generated"))
         }
      }
   }
}
