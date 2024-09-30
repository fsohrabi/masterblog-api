from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.storage.storage_json import StorageJson

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
storage = StorageJson()


@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = storage.list_blogs()
    return jsonify(posts)


@app.route('/api/posts', methods=['POST'])
def add():
    """
    Route for adding a new blog post.
    """
    data = request.get_json()
    if data and "title" in data and "content" in data and len(data['title']) != 0 and len(data['content']) != 0:
        title = data['title']
        content = data['content']
    else:
        return jsonify({"error": "Missing Credentials", }), 400

    storage.add_blog(title, content)
    posts = storage.list_blogs()
    return jsonify(posts[-1], 201)


@app.route('/api/posts/<int:post_id>', methods=['delete'])
def delete(post_id):
    """
    Route for deleting a blog post by its post ID.
    """
    storage.delete_blog(post_id)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
