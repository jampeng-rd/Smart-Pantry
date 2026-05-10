# 外部行動裝置串接規範

本 repo 先不撰寫 Android 或 iOS App，只提供 Smart Pantry 後端 API 與未來手機 App / PWA 串接注意事項。

禁止建立 `android/` App 原始碼、Gradle Android project、Android build workflow、Android UI / ViewModel / Repository 實作。

手機真機測試時，若後端跑在開發機，手機不能用 `localhost`，需使用區網 IP，例如 `http://192.168.1.10:8000`。手機與開發機需在同一 Wi-Fi 或可互相連線。

未來手機 App 可能功能：拍攝食材照片、拍攝餐點照片、查看購物清單、查看即將過期提醒。目前本 repo 優先以 Web UI 完成功能。
