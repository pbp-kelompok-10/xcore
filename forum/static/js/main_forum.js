
$(document).ready(function () {
    // Load posts saat halaman dimuat
    displayPosts();

    $("#postForm").on('submit', function(event) {
        event.preventDefault();

        let postContent = $("#postContent").val().trim();
        
        // Validasi input
        if (!postContent) {
            alert("Please write something!");
            return;
        }

        // Kirim POST request
        $.ajax({
            type: "POST",
            url: `/forum/${forumId}/add_post/`,  // Ganti dengan URL endpoint create post Anda
            data: {
                'message': postContent,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()  // CSRF Token
            },
            success: function (data) {
                $("#postContent").val('');  // Clear textarea
                displayPosts();  // Reload posts
                console.log("Post created successfully!");
            },
            error: function (xhr, status, error) {
                console.error("Error:", error);
                alert("Error sending post.");
            }
        });
    });

    $(document).on('click', '.delete-post', function(e) {
        e.preventDefault();
        let postId = $(this).data('post-id');
        deletePost(postId);
    });

    function deletePost(postId) {
        $.ajax({
            type: "POST",
            url: `/forum/${forumId}/delete_post/${postId}/`,
            data: {
                'forum_id': forumId,
                'post_id': postId,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()  // CSRF Token
            },
            success: function (data) {
                displayPosts();  // Reload posts
                console.log("Post deleted successfully!");
            },
            error: function (xhr, status, error) {
                console.error("Error:", error);
                alert("Error deleting post.");
            }
        });
    }

    // Fungsi untuk menampilkan posts
    function displayPosts() {
        $.ajax({
            url: `/forum/${forumId}/get_posts/`,
            type: "GET",
            success: function(response) {
                $('#postsContainer').empty();
                
                console.log("Response posts:", response.posts); // Debug
                
                if (response.posts && response.posts.length > 0) {
                    response.posts.forEach(function(post) {
                        let deleteButton = '';
                        if (response.user_is_authenticated && response.user_id == post.author_id) {
                            deleteButton = `<button class="btn btn-danger btn-sm delete-post" data-post-id="${post.id}">Delete</button>`;
                        }

                        var postHtml = `
                            <div class="match-card">
                                
                                <div class="score-section">
                                    <div class="post-authorname">${post.author_name}</div>
                                    <div class="score">${post.message}</div>
                                    <div class="match-info">Posted on ${post.created_at}</div>
                                    <div class="post-actions">
                                        ${deleteButton}
                                    </div>
                                </div>
                            </div>
                        `;
                        $('#postsContainer').append(postHtml);  // GANTI KE postsContainer
                    });
                } else {
                    $('#postsContainer').html('<p>No posts yet.</p>');
                }
            },
            error: function(xhr, status, error) {
                console.error("Error loading posts:", error);
                $('#postsContainer').html('<p>Error loading posts.</p>');
            }
        });
    }
});