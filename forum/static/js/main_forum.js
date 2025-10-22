
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
                        console.log("Loading post by:", post.author_name); // Debug
                        
                        var postHtml = `
                            <div class="match-card">
                                
                                <div class="score-section">
                                    <div class="post-authorname">${post.author_name}</div>
                                    <div class="score">${post.message}</div>
                                    <div class="match-info">Posted on ${post.created_at}</div>
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