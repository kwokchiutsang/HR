#!/usr/bin/env python3
"""
自動將 index16.html 轉換為 Firebase Firestore 整合版本
使用方法：python convert_to_firebase.py
"""

import re

# Firebase SDK 和配置代碼（插入到 </head> 之前）
FIREBASE_SDK = '''<!-- Firebase SDK -->
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
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Firestore 數據操作封裝
const FirestoreDB = {
  async setItem(key, value) {
    try {
      await db.collection('hr-data').doc(key).set({
        value: value,
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
      });
      console.log(`✅ Firestore saved: ${key}`);
    } catch (error) {
      console.error(`❌ Firestore error (${key}):`, error);
      localStorage.setItem(key, value); // 失敗時使用 localStorage 備份
    }
  },

  async getItem(key) {
    try {
      const doc = await db.collection('hr-data').doc(key).get();
      if (doc.exists) {
        console.log(`✅ Firestore loaded: ${key}`);
        return doc.data().value;
      }
      return null;
    } catch (error) {
      console.error(`❌ Firestore error (${key}):`, error);
      return localStorage.getItem(key); // 失敗時使用 localStorage 備份
    }
  },

  async removeItem(key) {
    try {
      await db.collection('hr-data').doc(key).delete();
      console.log(`✅ Firestore deleted: ${key}`);
    } catch (error) {
      console.error(`❌ Firestore error (${key}):`, error);
      localStorage.removeItem(key);
    }
  },

  async clear() {
    try {
      const snapshot = await db.collection('hr-data').get();
      const batch = db.batch();
      snapshot.docs.forEach(doc => batch.delete(doc.ref));
      await batch.commit();
      console.log('✅ Firestore: all data cleared');
    } catch (error) {
      console.error('❌ Firestore clear error:', error);
      localStorage.clear();
    }
  }
};

console.log('🔥 Firebase initialized - Data will sync across devices');
</script>
'''

def convert_html_to_firebase(input_file='index16.html', output_file='index17.html'):
    """將 index16.html 轉換為 Firebase 版本"""
    
    print(f"📖 讀取 {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 在 </head> 前插入 Firebase SDK
    print("🔧 添加 Firebase SDK...")
    content = content.replace('</head>', f'{FIREBASE_SDK}\n</head>')
    
    # 2. 替換 localStorage.setItem 為 await FirestoreDB.setItem
    print("🔧 替換 localStorage.setItem...")
    content = re.sub(
        r'localStorage\.setItem\(',
        'await FirestoreDB.setItem(',
        content
    )
    
    # 3. 替換 localStorage.getItem 為 await FirestoreDB.getItem
    print("🔧 替換 localStorage.getItem...")
    content = re.sub(
        r'localStorage\.getItem\(',
        'await FirestoreDB.getItem(',
        content
    )
    
    # 4. 替換 localStorage.removeItem 為 await FirestoreDB.removeItem
    print("🔧 替換 localStorage.removeItem...")
    content = re.sub(
        r'localStorage\.removeItem\(',
        'await FirestoreDB.removeItem(',
        content
    )
    
    # 5. 替換 localStorage.clear() 為 await FirestoreDB.clear()
    print("🔧 替換 localStorage.clear...")
    content = re.sub(
        r'localStorage\.clear\(',
        'await FirestoreDB.clear(',
        content
    )
    
    # 6. 將包含數據操作的函數改為 async（簡單模式：在 function 前添加 async）
    print("🔧 將函數改為 async...")
    # 查找所有包含 await 的函數並添加 async
    content = re.sub(
        r'(\n\s*function\s+\w+\s*\([^)]*\)\s*\{[^}]*await\s)',
        r'\n    async function \1',
        content,
        flags=re.MULTILINE
    )
    
    # 7. 更新標題和版本號
    print("🔧 更新標題...")
    content = content.replace(
        'V67.4 複製視窗修正版',
        'V68.0 Firebase雲端同步版'
    )
    
    # 保存新文件
    print(f"💾 保存到 {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"""
✅ 轉換完成！

📄 輸出文件: {output_file}
📊 文件大小: {len(content):,} 字節

⚠️  重要提示：
1. 由於JavaScript的異步特性，部分函數可能需要手動調整
2. 請在本地瀏覽器測試所有功能
3. 確認無誤後再上傳到 GitHub

🧪 測試步驟：
1. 在本地打開 {output_file}
2. 打開瀏覽器控制台（F12）
3. 查看是否顯示 "🔥 Firebase initialized"
4. 測試添加/編輯員工數據
5. 在 Firebase Console 確認數據已保存

🌐 Firebase Console:
https://console.firebase.google.com/u/0/project/hr-system-58d4d/firestore

📤 上傳後訪問:
https://kwokchiutsang.github.io/HR/index17.html
    """)

if __name__ == '__main__':
    try:
        convert_html_to_firebase()
    except FileNotFoundError:
        print("""
❌ 錯誤：找不到 index16.html

請確保：
1. 已下載 index16.html 到當前目錄
2. 在包含 index16.html 的目錄中運行此腳本

下載命令：
curl -O https://raw.githubusercontent.com/kwokchiutsang/HR/main/index16.html

然後再運行：
python convert_to_firebase.py
        """)
    except Exception as e:
        print(f"❌ 錯誤: {e}")
