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
    if storage.delete_blog(post_id):
        return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200
    return jsonify({"error": "Post was not found", }), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update(post_id):
    """
    Route for update blog post by id .
    """
    data = request.get_json()
    if data or ("title" in data and len(data['title']) != 0) or ("content" in data and len(data['content']) != 0):
        title = data['title'] if "title" in data else None
        content = data['content'] if "content" in data else None
    else:
        return jsonify({"error": "Missing Credentials", }), 400

    update_result = storage.update_blog(post_id, title, content)
    if not update_result:
        return jsonify({"error": "Post was not found", }), 404
    return jsonify(update_result, 201)


@app.route('/api/posts/search', methods=['get'])
def search():
    """
        Route for searching blog posts by title or content.
        Returns posts where either the title or content contains the search terms.
        If no search parameters are provided, return an empty list.
        """
    title = request.args.get('title')
    content = request.args.get('content')
    posts = storage.list_blogs()
    if not title and not content:
        return jsonify([]), 200
    filtered_posts = []

    for post in posts:
        # If both title and content are provided
        if title and content:
            if (title.lower() in post['title'].lower()) and (content.lower() in post['content'].lower()):
                filtered_posts.append(post)
        elif title:
            if title.lower() in post['title'].lower():
                filtered_posts.append(post)
        elif content:
            if content.lower() in post['content'].lower():
                filtered_posts.append(post)
    return jsonify(filtered_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
