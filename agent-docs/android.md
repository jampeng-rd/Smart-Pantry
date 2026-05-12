# 外部行動裝置串接規範

本 repo 先不撰寫 Android 或 iOS App，只提供 Smart Pantry 後端 API 與未來手機 App / PWA 串接注意事項。

禁止建立 `android/` App 原始碼、Gradle Android project、Android build workflow、Android UI / ViewModel / Repository 實作。

手機真機測試時，若後端跑在開發機，手機不能用 `localhost`，需使用區網 IP，例如 `http://192.168.1.10:8000`。手機與開發機需在同一 Wi-Fi 或可互相連線。

未來手機 App 可能功能：拍攝食材照片、拍攝餐點照片、查看購物清單、查看即將過期提醒。目前本 repo 優先以 Web UI 完成功能。


## 未來手機通知規劃

到期提醒規則應由 server 端管理，包含不提醒、前 1 天（預設）、前 3 天，以及上午 8:00 / 下午 5:00 的提醒時段。未來手機 App 可提供 push token，server 根據同一套使用者設定決定何時推播；手機端只負責顯示原生通知與管理系統通知權限。
