# INDEX20.html Firebase 連接指南

## 概述
此指南說明如何為 index20.html (V72.0 每日支出明細版) 添加 Firebase Firestore 雲端同步功能。

## Firebase 項目資料
- 項目 ID: hr-system-58d4d
- 項目名稱: HR-System
- Firebase Console: https://console.firebase.google.com/project/hr-system-58d4d

## 修改步驟

### 1. 在 `<head>` 標籤內添加 Firebase SDK（在現有 JS Libraries 之後）

```html
<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore-compat.js"></script>
```

### 2. 在 Vue 應用啟動之前初始化 Firebase（在 `<script>` 標籤內，createApp 之前）

```javascript
// Firebase 配置
const firebaseConfig = {
  apiKey: "AIzaSyDMXQZE7C1BqLaOy5l-c93YvANB_-wl0qE",
  authDomain: "hr-system-58d4d.firebaseapp.com",
  projectId: "hr-system-58d4d",
  storageBucket: "hr-system-58d4d.firebasestorage.app",
  messagingSenderId: "590962476838",
  appId: "1:590962476838:web:2ede3d3cc6f8b1c0a9e7dd"
};

// 初始化 Firebase
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();
```

### 3. 在 Vue data() 中添加 Firebase 狀態

在現有的 data() return 對象中添加：

```javascript
// Firebase 狀態
isSyncing: false,
lastSyncTime: null,
syncError: null,
```

### 4. 在 methods 中添加 Firebase 同步方法

```javascript
// ============ Firebase 同步方法 ============
async saveToFirebase(collectionName, data) {
  try {
    this.isSyncing = true;
    await db.collection(collectionName).doc('main').set(data);
    this.lastSyncTime = new Date().toLocaleString();
    this.syncError = null;
  } catch (error) {
    console.error('Firebase 儲存失敗:', error);
    this.syncError = error.message;
  } finally {
    this.isSyncing = false;
  }
},

async loadFromFirebase(collectionName) {
  try {
    const doc = await db.collection(collectionName).doc('main').get();
    if (doc.exists) {
      return doc.data();
    }
    return null;
  } catch (error) {
    console.error('Firebase 讀取失敗:', error);
    this.syncError = error.message;
    return null;
  }
},

async syncAllData() {
  this.isSyncing = true;
  try {
    // 儲存所有資料到 Firebase
    await Promise.all([
      this.saveToFirebase('staffList', this.staffList),
      this.saveToFirebase('schoolList', this.schoolList),
      this.saveToFirebase('events', this.events),
      this.saveToFirebase('rosterData', this.rosterData),
      this.saveToFirebase('presets', {
        holiday: this.holidayPresets,
        memo: this.memoPresets,
        leave: this.leavePresets,
        rosterNote: this.rosterNotePresets,
        time: this.timePresets
      })
    ]);
    this.showModal('資料已同步至雲端', 'info');
  } catch (error) {
    this.showModal('同步失敗: ' + error.message, 'info');
  } finally {
    this.isSyncing = false;
  }
},

async loadAllData() {
  this.isSyncing = true;
  try {
    const [staffData, schoolData, eventsData, rosterDataFB, presetsData] = await Promise.all([
      this.loadFromFirebase('staffList'),
      this.loadFromFirebase('schoolList'),
      this.loadFromFirebase('events'),
      this.loadFromFirebase('rosterData'),
      this.loadFromFirebase('presets')
    ]);
    
    if (staffData) this.staffList = staffData;
    if (schoolData) this.schoolList = schoolData;
    if (eventsData) this.events = eventsData;
    if (rosterDataFB) this.rosterData = rosterDataFB;
    if (presetsData) {
      if (presetsData.holiday) this.holidayPresets = presetsData.holiday;
      if (presetsData.memo) this.memoPresets = presetsData.memo;
      if (presetsData.leave) this.leavePresets = presetsData.leave;
      if (presetsData.rosterNote) this.rosterNotePresets = presetsData.rosterNote;
      if (presetsData.time) this.timePresets = presetsData.time;
    }
    
    this.showModal('已從雲端載入資料', 'info');
  } catch (error) {
    this.showModal('載入失敗: ' + error.message, 'info');
  } finally {
    this.isSyncing = false;
  }
},

// 修改現有的 doLogin 方法，登入後自動載入雲端資料
async doLogin() { 
  if(this.loginData.id === 'philip' && this.loginData.pw === '60986314') { 
    this.isLoggedIn = true; 
    this.loginError = false;
    // 自動載入雲端資料
    await this.loadAllData();
  } else { 
    this.loginError = true; 
  } 
},
```

### 5. 在側邊欄添加同步按鈕

在 `.sidebar` 的 `<nav>` 中添加：

```html
<a class="nav-link" @click="syncAllData">
  <i class="bi bi-cloud-upload"></i> 
  <span v-if="isSyncing">同步中...</span>
  <span v-else>同步至雲端</span>
</a>
<a class="nav-link" @click="loadAllData">
  <i class="bi bi-cloud-download"></i> 從雲端載入
</a>
```

### 6. 移動端導航也添加同步選項

在 `#mobileMenu` 的 `<ul>` 中添加：

```html
<li class="nav-item"><a class="nav-link" @click="syncAllData">
  <span v-if="isSyncing">同步中...</span>
  <span v-else>同步至雲端</span>
</a></li>
<li class="nav-item"><a class="nav-link" @click="loadAllData">從雲端載入</a></li>
```

### 7. 添加自動同步（可選）

在需要同步的操作後調用 `saveToFirebase`，例如：

```javascript
// 在 addEvent 後
async addEvent() { 
  if(!this.newEvent.date || !this.newEvent.note) return this.showModal('資料不全', 'info'); 
  this.events.push({...this.newEvent}); 
  await this.saveToFirebase('events', this.events); // 自動同步
  this.showModal('已新增', 'info'); 
},

// 在 addRoster 後（proceed 函數內）
await this.saveToFirebase('rosterData', this.rosterData);

// 在 addStaff 後
await this.saveToFirebase('staffList', this.staffList);

// 在 addSchool 後
await this.saveToFirebase('schoolList', this.schoolList);
```

## 測試步驟

1. 登入系統（會自動載入雲端資料）
2. 修改任何資料（員工、學校、排班等）
3. 點擊「同步至雲端」按鈕
4. 在另一個設備或瀏覽器登入
5. 點擊「從雲端載入」按鈕
6. 確認資料已同步

## 注意事項

1. **Firebase 安全規則**：需要在 Firebase Console 中設置 Firestore 規則，目前為測試模式（公開讀寫）
2. **網絡連接**：需要網絡連接才能同步
3. **數據結構**：確保數據結構一致性
4. **錯誤處理**：已包含基本錯誤處理和用戶提示

## 完整的修改文件

由於 index20.html 文件較大，建議：
1. 複製 index20.html 為 index21.html
2. 按照上述步驟逐步添加 Firebase 功能
3. 測試確認無誤後部署

## 相關文件

- FIREBASE_GUIDE.md - Firebase 基礎配置指南
- INDEX16_FIREBASE_MODIFICATION.md - 之前版本的 Firebase 整合參考
- convert_to_firebase.py - Python 轉換腳本（可用於批量處理）

---

**最後更新**: 2025-12-10
**版本**: V72 Firebase Integration Guide
