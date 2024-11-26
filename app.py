import json
import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 設定 JSON 檔案路徑
POSTS_FILE = 'posts.json'
UPLOAD_FOLDER = 'static/uploads'  # 設定圖片上傳目錄
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 確保 uploads 目錄存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 判斷檔案是否為允許的圖片格式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 讀取 JSON 文件的文章數據
def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# 寫入 JSON 文件
def save_posts(posts):
    with open(POSTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    """首頁 - 自我介紹"""
    about = "希望記錄下旅行中的點點滴滴，給未來的自己回味!"
    return render_template('index.html', about=about)

@app.route('/posts')
def posts_list():
    """顯示文章列表"""
    posts = load_posts()  # 從 JSON 讀取文章
    return render_template('posts.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    """顯示單篇文章"""
    posts = load_posts()
    post = posts[post_id]
    return render_template('post.html', post=post, post_id=post_id)

@app.route('/create', methods=['GET', 'POST'])
def create():
    """新增文章"""
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        date = request.form['date']
        image = None
        
        # 處理圖片上傳
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                image_filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))
                image = image_filename
        
        # 儲存文章數據
        posts = load_posts()  # 從 JSON 讀取文章
        posts.append({'title': title, 'author': author, 'content': content, 'date': date, 'image': image})
        save_posts(posts)  # 儲存回 JSON 文件
        return redirect(url_for('posts_list'))
    
    return render_template('create.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    """編輯文章"""
    posts = load_posts()
    post = posts[post_id]
    if request.method == 'POST':
        post['title'] = request.form['title']
        post['author'] = request.form['author']
        post['content'] = request.form['content']
        post['date'] = request.form['date']
        
        # 處理圖片上傳
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                image_filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))
                post['image'] = image_filename  # 更新圖片
        
        save_posts(posts)  # 儲存回 JSON 文件
        return redirect(url_for('post', post_id=post_id))
    
    return render_template('edit.html', post=post)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/delete/<int:post_id>')
def delete(post_id):
    """刪除文章"""
    posts = load_posts()
    posts.pop(post_id)
    save_posts(posts)  # 儲存回 JSON 文件
    return redirect(url_for('posts_list'))

if __name__ == '__main__':
    app.run(debug=True)