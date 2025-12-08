# index16.html Firebase 整合修改指南

## 概述
本文檔提供詳細的步驟，將 index16.html 的 localStorage 存儲替換為 Firebase Firestore，實現跨地點數據同步。

## Firebase 配置信息
**項目ID**: hr-system-58d4d
**應用**: HR-Web

## 修改步驟

### 步驟 1：添加 Firebase SDK（在 </head> 標籤之前）

找到第 14 行的 `</head>` 標籤，在它之前添加以下代碼：

```html
<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore-compat.js"></script>

<script>
// Firebase 配置
const firebaseConfig = {
  apiKey: "AIzaSyDuVyoeMYvgD8X_aMYwJRQc-j2k_04_DqrYM9s",
  authDomain: "hr-system-58d4d.firebaseapp.com",
  projectId: "hr-system-58d4d",
  storageBucket: "hr-system-58d4d.firebasestorage.app",
  messagingSenderId: "841414140594",
  appId: "1:841414140594:web:070909fd863379d18bd5fab",
  measurementId: "G-7LMGNJNYBm"
};

// 初始化 Firebase
const app = firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Firestore 數據操作封裝函數
const FirestoreDB = {
  // 保存數據
  async setItem(key, value) {
    try {
      await db.collection('hr-data').doc(key).set({
        value: value,
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
      });
      console.log(`Firestore setItem: ${key}`);
    } catch (error) {
      console.error(`Firestore setItem error (${key}):`, error);
      // 失敗時使用 localStorage 作為備份
      localStorage.setItem(key, value);
    }
  },

  // 讀取數據
  async getItem(key) {
    try {
      const doc = await db.collection('hr-data').doc(key).get();
      if (doc.exists) {
        console.log(`Firestore getItem: ${key}`);
        return doc.data().value;
      }
      return null;
    } catch (error) {
      console.error(`Firestore getItem error (${key}):`, error);
      // 失敗時使用 localStorage 作為備份
      return localStorage.getItem(key);
    }
  },

  // 刪除數據
  async removeItem(key) {
    try {
      await db.collection('hr-data').doc(key).delete();
      console.log(`Firestore removeItem: ${key}`);
    } catch (error) {
      console.error(`Firestore removeItem error (${key}):`, error);
      localStorage.removeItem(key);
    }
  },

  // 清空所有數據
  async clear() {
    try {
      const snapshot = await db.collection('hr-data').get();
      const batch = db.batch();
      snapshot.docs.forEach(doc => {
        batch.delete(doc.ref);
      });
      await batch.commit();
      console.log('Firestore clear: all data');
    } catch (error) {
      console.error('Firestore clear error:', error);
      localStorage.clear();
    }
  }
};

// 頁面加載時初始化
window.addEventListener('DOMContentLoaded', function() {
  console.log('Firebase initialized successfully');
  console.log('Firestore DB ready for:', firebaseConfig.projectId);
});
</script>
```

### 步驟 2：替換 localStorage 調用

需要將文件中所有的 localStorage 調用替換為 FirestoreDB 的異步調用。

#### 2.1 查找所有 localStorage.setItem() 調用

搜索模式：`localStorage.setItem(`

替換為：`await FirestoreDB.setItem(`

**注意**：包含此調用的函數需要添加 `async` 關鍵字

#### 2.2 查找所有 localStorage.getItem() 調用

搜索模式：`localStorage.getItem(`

替換為：`await FirestoreDB.getItem(`

**注意**：包含此調用的函數需要添加 `async` 關鍵字

#### 2.3 查找所有 localStorage.removeItem() 調用

搜索模式：`localStorage.removeItem(`

替換為：`await FirestoreDB.removeItem(`

#### 2.4 查找所有 localStorage.clear() 調用

搜索模式：`localStorage.clear(`

替換為：`await FirestoreDB.clear(`

### 步驟 3：關鍵函數異步化

由於 Firestore 操作是異步的，需要將包含數據操作的函數改為 async 函數。

#### 主要需要修改的函數（搜索並添加 async）：

1. 所有保存數據的函數
2. 所有讀取數據的函數  
3. 事件處理函數中調用數據操作的部分

**示例**：
```javascript
// 原來：
function saveEmployees() {
    localStorage.setItem('employees', JSON.stringify(employees));
}

// 修改後：
async function saveEmployees() {
    await FirestoreDB.setItem('employees', JSON.stringify(employees));
}
```

### 步驟 4：初始化數據加載

找到頁面初始化的地方（通常在 window.onload 或 DOMContentLoaded），確保數據加載使用異步方式：

```javascript
// 原來：
window.addEventListener('DOMContentLoaded', function() {
    const data = localStorage.getItem('employees');
    // ...處理數據
});

// 修改後：
window.addEventListener('DOMContentLoaded', async function() {
    const data = await FirestoreDB.getItem('employees');
    // ...處理數據
});
```

### 步驟 5：錯誤處理

在關鍵的數據操作位置添加 try-catch 錯誤處理：

```javascript
async function saveData() {
    try {
        await FirestoreDB.setItem('key', 'value');
        console.log('數據保存成功');
    } catch (error) {
        console.error('數據保存失敗:', error);
        alert('數據保存失敗，請檢查網絡連接');
    }
}
```

## 測試步驟

1. **本地測試**：
   - 在本地瀏覽器中打開修改後的 index16.html
   - 打開瀏覽器控制台查看 Firebase 連接狀態
   - 測試數據保存和讀取功能

2. **Firebase Console 驗證**：
   - 訪問 https://console.firebase.google.com
   - 進入 HR-System 項目
   - 查看 Firestore Database → hr-data collection
   - 確認數據正確保存

3. **跨設備測試**：
   - 在不同設備上打開系統
   - 在一台設備上修改數據
   - 刷新另一台設備，確認數據已同步

## 部署

修改完成並測試通過後：

1. 提交到 GitHub：
```bash
git add index16.html
git commit -m "將 localStorage 替換為 Firebase Firestore"
git push origin main
```

2. GitHub Pages 會自動部署
3. 訪問 https://kwokchiutsang.github.io/HR/index16.html 驗證

## 重要提示

⚠️ **數據遷移**：
- 修改後首次使用時，原有 localStorage 的數據不會自動遷移
- 如需保留舊數據，請在修改前備份 localStorage 數據
- 或添加數據遷移代碼，在首次加載時將 localStorage 數據同步到 Firestore

⚠️ **性能考慮**：
- Firestore 有讀寫配額限制（免費版：每天 50,000 次讀取，20,000 次寫入）
- 建議在適當的地方添加數據緩存機制
- 避免頻繁的小批量寫入，考慮批量操作

⚠️ **安全規則**：
- 當前配置僅供開發測試使用
- 生產環境需要在 Firebase Console 配置適當的安全規則
- 建議添加用戶認證機制

## 參考文檔

- Firebase Firestore 文檔: https://firebase.google.com/docs/firestore
- 您之前成功整合的 index7.html 可作為參考
- FIREBASE_GUIDE.md 提供了詳細的 Firebase 配置說明

## 聯絡支持

如有問題，請參考：
- Firebase Console: https://console.firebase.google.com/u/0/project/hr-system-58d4d
- Firestore Dashboard: https://console.firebase.google.com/u/0/project/hr-system-58d4d/firestore
