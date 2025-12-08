# index16.html Firebase 集成指南

## 🎯 目標
將 index16.html 連接到 Firebase Firestore，實現跨設備數據同步。

## 📋 前置準備

### 1. 創建 Firebase 項目
1. 訪問 [Firebase Console](https://console.firebase.google.com/)
2. 點擊「添加項目」
3. 輸入項目名稱（例如：philip-cleaning-hr）
4. 完成創建流程

### 2. 啟用 Firestore 數據庫
1. 在 Firebase Console 左側選單選擇「Firestore Database」
2. 點擊「創建數據庫」
3. 選擇「測試模式」（開發階段）
4. 選擇地區：asia-east2 (香港)

### 3. 獲取 Firebase 配置
1. 點擊項目設置 ⚙️
2. 在「您的應用」部分選擇「Web 應用」(</>) 
3. 複製 firebaseConfig 對象

---

## 🔧 代碼修改步驟

### 步驟 1：添加 Firebase SDK

在 index16.html 的 `</head>` 標籤之前（約第 14 行）添加：

```html
<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore-compat.js"></script>
```

### 步驟 2：初始化 Firebase

在 `const { createApp } = Vue;` 之後（約第 628 行），添加：

```javascript
// ========== Firebase 初始化 ==========
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();
console.log("✅ Firebase 已初始化");
```

### 步驟 3：添加 mounted 生命週期

在 Vue createApp 的 `data()` 後面添加：

```javascript
mounted() {
  console.log("🚀 系統啟動中...");
  this.loadFromFirebase();
  this.setupRealtimeSync();
},
```

### 步驟 4：添加 Firebase 同步方法

在 `methods: {` 後面添加以下方法：

```javascript
// ========== Firebase 數據載入 ==========
async loadFromFirebase() {
  try {
    console.log("📥 正在從 Firebase 載入數據...");
    
    // 載入學校數據
    const schoolsSnap = await db.collection('schools').get();
    if (!schoolsSnap.empty) {
      this.schoolList = schoolsSnap.docs.map(doc => doc.data());
      console.log(`✅ 載入 ${this.schoolList.length} 間學校`);
    }
    
    // 載入員工數據
    const staffSnap = await db.collection('staff').get();
    if (!staffSnap.empty) {
      this.staffList = staffSnap.docs.map(doc => doc.data());
      console.log(`✅ 載入 ${this.staffList.length} 位員工`);
    }
    
    // 載入事件數據
    const eventsSnap = await db.collection('events').get();
    if (!eventsSnap.empty) {
      this.events = eventsSnap.docs.map(doc => doc.data());
      console.log(`✅ 載入 ${this.events.length} 個事件`);
    }
    
    // 載入排班數據
    const rostersSnap = await db.collection('rosters').get();
    if (!rostersSnap.empty) {
      this.rosterData = rostersSnap.docs.map(doc => doc.data());
      console.log(`✅ 載入 ${this.rosterData.length} 筆排班`);
    }
    
    console.log("✅ 所有數據已同步");
  } catch (error) {
    console.error("❌ 載入失敗:", error);
    alert("無法連接 Firebase，請檢查網絡或配置");
  }
},

// ========== 實時同步監聽 ==========
setupRealtimeSync() {
  console.log("🔄 啟動實時同步...");
  
  // 監聽學校變化
  db.collection('schools').onSnapshot(snapshot => {
    this.schoolList = snapshot.docs.map(doc => doc.data());
  });
  
  // 監聽員工變化
  db.collection('staff').onSnapshot(snapshot => {
    this.staffList = snapshot.docs.map(doc => doc.data());
  });
  
  // 監聽事件變化
  db.collection('events').onSnapshot(snapshot => {
    this.events = snapshot.docs.map(doc => doc.data());
  });
  
  // 監聽排班變化
  db.collection('rosters').onSnapshot(snapshot => {
    this.rosterData = snapshot.docs.map(doc => doc.data());
  });
  
  console.log("✅ 實時同步已啟動");
},

// ========== 同步到 Firebase ==========
async syncToFirebase(collection, item) {
  try {
    const docId = item.id.toString();
    await db.collection(collection).doc(docId).set(item);
    console.log(`✅ 已同步: ${collection}/${docId}`);
  } catch (error) {
    console.error(`❌ 同步失敗:`, error);
  }
},

// ========== 從 Firebase 刪除 ==========
async deleteFromFirebase(collection, id) {
  try {
    await db.collection(collection).doc(id.toString()).delete();
    console.log(`✅ 已刪除: ${collection}/${id}`);
  } catch (error) {
    console.error(`❌ 刪除失敗:`, error);
  }
},
```

### 步驟 5：修改現有方法（示例）

找到以下方法並添加同步邏輯：

#### addSchool (約第 XXX 行)
```javascript
async addSchool() {
  if(this.newSchoolName) {
    const school = {
      id: 'SCH' + (this.schoolList.length + 1), 
      name: this.newSchoolName
    };
    this.schoolList.push(school);
    await this.syncToFirebase('schools', school);  // 新增這行
  }
  this.newSchoolName = '';
},
```

#### addStaff (約第 XXX 行)
```javascript
async addStaff() {
  if(this.newStaff.name) {
    const staff = {
      id: 'S' + (this.staffList.length + 1), 
      ...this.newStaff
    };
    this.staffList.push(staff);
    await this.syncToFirebase('staff', staff);  // 新增這行
  }
  this.newStaff.name = ''; 
  this.newStaff.defaultSchoolId = '';
},
```

#### addEvent (約第 XXX 行)
```javascript
async addEvent() {
  if(!this.newEvent.date || !this.newEvent.note) return alert('資料不全');
  const event = {...this.newEvent, id: Date.now().toString()};
  this.events.push(event);
  await this.syncToFirebase('events', event);  // 新增這行
  alert('已新增');
},
```

#### addRoster (約第 XXX 行)
在 `this.rosterData.push({...})` 後面添加：
```javascript
await this.syncToFirebase('rosters', {最後添加的排班對象});
```

#### removeSchool, removeStaff, deleteEvent 等刪除方法
添加：
```javascript
await this.deleteFromFirebase('對應集合名', id);
```

---

## 🚀 測試步驟

### 1. 本地測試
1. 下載修改後的 index16.html
2. 用瀏覽器打開
3. 打開開發者工具 Console (F12)
4. 檢查是否看到：
   ```
   ✅ Firebase 已初始化
   🚀 系統啟動中...
   📥 正在從 Firebase 載入數據...
   ✅ 載入 X 間學校
   ...
   ```

### 2. 驗證同步
1. 在「資料庫設定」添加一間學校
2. 打開 Firebase Console > Firestore Database
3. 檢查 `schools` 集合是否有新數據
4. 在另一台設備打開網頁
5. 驗證數據是否自動出現

### 3. 實時同步測試
1. 在設備 A 添加員工
2. 在設備 B 觀察是否自動更新（無需刷新頁面）

---

## ⚙️ Firestore 安全規則（生產環境）

開發完成後，更新 Firestore 規則：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 只允許認證用戶讀寫
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

---

## 📊 數據結構

### schools 集合
```json
{
  "id": "SCH01",
  "name": "香港大學"
}
```

### staff 集合
```json
{
  "id": "S001",
  "name": "陳大文",
  "role": "隊長",
  "defaultSchoolId": "SCH01",
  "leaveTotal": 12
}
```

### events 集合
```json
{
  "date": "2025-12-09",
  "type": "leave",
  "staffId": "S001",
  "schoolId": "SCH01",
  "note": "年假"
}
```

### rosters 集合
```json
{
  "id": 1,
  "date": "2025-12-09",
  "staffId": "S001",
  "schoolId": "SCH01",
  "startTime": "09:00",
  "endTime": "18:00",
  "jobContent": "一般清潔",
  "note": "",
  "wage": 600,
  "transport": 50
}
```

---

## ✅ 完成檢查清單

- [ ] 創建 Firebase 項目
- [ ] 啟用 Firestore 數據庫
- [ ] 獲取並填入 Firebase 配置
- [ ] 添加 Firebase SDK
- [ ] 添加初始化代碼
- [ ] 添加 mounted 生命週期
- [ ] 添加 Firebase 同步方法
- [ ] 修改所有數據操作方法
- [ ] 本地測試成功
- [ ] 跨設備同步測試成功
- [ ] 上傳到 GitHub
- [ ] 生產環境部署

---

## 🆘 常見問題

### Q: 顯示「無法連接 Firebase」
**A:** 檢查：
1. Firebase 配置是否正確填入
2. 網絡連接是否正常
3. Firestore 數據庫是否已啟用

### Q: 數據沒有同步
**A:** 檢查：
1. Console 是否有錯誤訊息
2. Firebase Console 中數據是否存在
3. 方法是否添加了 `await this.syncToFirebase()`

### Q: 實時同步不工作
**A:** 確認 `setupRealtimeSync()` 已在 mounted 中調用

---

## 📞 技術支持

如有問題，請檢查：
1. Browser Console (F12) 錯誤訊息
2. Firebase Console > Firestore Database 數據
3. 網絡連接狀態

---

**最後更新：2025-12-09**
**版本：V67.4 → V68.0 (Firebase 集成版)**
