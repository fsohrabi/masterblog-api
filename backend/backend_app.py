from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import ValidationError

from backend.storage.storage_json import StorageJson
from backend.schemas import PostSchema, PostUpdateSchema, QueryParamSchema

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
storage = StorageJson()

SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'  #
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Fetch and return blog posts, sorted by query parameters.

    Query Params:
    - sort (optional): Sort by 'id', 'title', or 'content'. Defaults to 'id'.
    - direction (optional): 'asc' for ascending, 'desc' for descending. Defaults to 'desc'.

    Returns:
    - 200: JSON list of sorted posts.
    - 400: Error if invalid query parameters are provided.

    Example:
    /api/posts?sort=title&direction=asc
    """
    schema = QueryParamSchema()
    arguments = request.args
    try:
        # Validate and deserialize query parameters
        validated_args = schema.load(arguments)
        sort_value = validated_args.get('sort', 'id')
        direction_value = validated_args.get('direction', 'desc')
        reverse_freq = {'desc': False, 'asc': True}
        posts = storage.list_blogs()
        sorted_posts = sorted(posts, key=lambda post: post.get(sort_value, ''), reverse=reverse_freq[direction_value])
        return jsonify(sorted_posts), 200

    except ValidationError as err:
        return jsonify(err.messages), 400


@app.route('/api/posts', methods=['POST'])
def add():
    """
    Route for adding a new blog post.
    """
    post_schema = PostSchema()
    try:
        data = post_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    storage.add_blog(data['title'], data['content'], data['author'])
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
    post_update_schema = PostUpdateSchema()
    try:
        data = post_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    title = data.get('title', None)
    content = data.get('content', None)
    author = data.get('author', None)
    update_result = storage.update_blog(post_id, title, content, author)
    if not update_result:
        return jsonify({"error": "Post was not found", }), 404
    return jsonify(update_result, 201)


def filter_posts(posts, filters):
    """Filter posts based on the provided filters (title, content, author)."""
    filtered_posts = []
    # Iterate through posts and apply filters
    query = ""
    for post in posts:
        for key, value in filters.items():
            if key in post:
                if len(query) != 0:
                    query += f' and "{value}" in post["{key}"]'
                else:
                    query += f'"{value}" in post["{key}"]'
            else:
                break

    filtered_posts = [post for post in posts if eval(query)]
    return filtered_posts


@app.route('/api/posts/search', methods=['get'])
def search():
    """
    Route for searching blog posts by title or content,author.
    Returns posts where either the title or content contains the search terms.
    If no search parameters are provided, return an empty list.
    """
    filters = {key: value for key, value in request.args.items() if value}
    posts = storage.list_blogs()
    if not filters:
        return jsonify([]), 200
    filtered_posts = filter_posts(posts, filters)
    return jsonify(filtered_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
