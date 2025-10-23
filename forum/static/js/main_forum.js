$(document).ready(function () {
    displayPosts();

    // Add New Post
    $("#postForm").on('submit', function(event) {
        event.preventDefault();
        let postContent = $("#postContent").val().trim();
        
        if (!postContent) {
            alert("Please write something!");
            return;
        }

        $.ajax({
            type: "POST",
            url: `/forum/${forumId}/add_post/`,
            data: {
                'message': postContent,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                $("#postContent").val('');
                displayPosts();
            },
            error: function (xhr, status, error) {
                alert("Error sending post.");
            }
        });
    });

    // Edit Post Trigger
    $(document).on('click', '.edit-post', function(e) {
        e.preventDefault();
        let postId = $(this).data('post-id');
        let $postCard = $(this).closest('.match-card');
        
        // **CLOSE ALL OTHER EDITS**
        $('.edit-mode').removeClass('active');
        $('.post-display').removeClass('editing');
        
        // **TOGGLE CURRENT**
        $postCard.find('.post-display').toggleClass('editing');
        $postCard.find('.edit-mode').toggleClass('active');
    });

    // Save Post Trigger
    $(document).on('click', '.save-edit', function(e) {
        e.preventDefault();
        let postId = $(this).data('post-id');
        let newMessage = $(this).closest('.edit-mode').find('textarea').val().trim();
        let $postCard = $(this).closest('.match-card');
        
        if (!newMessage) {
            alert("Message cannot be empty!");
            return;
        }

        console.log("Editing post ID:", postId, "New message:", newMessage);
        
        editPost(postId, newMessage, $postCard);  
    });

    // Cancel Edit Trigger
    $(document).on('click', '.cancel-edit', function(e) {
        e.preventDefault();
        let $postCard = $(this).closest('.match-card');
        $postCard.find('.post-display').removeClass('editing');
        $postCard.find('.edit-mode').removeClass('active');
    });

    // Escape Key Trigger
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('.post-display').removeClass('editing');
            $('.edit-mode').removeClass('active');
        }
    });

    // Delete Post Trigger
    $(document).on('click', '.delete-post', function(e) {
        e.preventDefault();
        let postId = $(this).data('post-id');
        
        Swal.fire({ // kenapa swall nya ga terdefinisi
            title: 'Yakin ingin menghapus?',
            text: "Postingan ini akan dihapus secara permanen.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Ya, hapus!',
            cancelButtonText: 'Batal'
        }).then((result) => {
            if (result.isConfirmed) {
                deletePost(postId);
            }
        });
    });
    

    // Edit Post Function
    function editPost(postId, newMessage, $postCard) { 
        $.ajax({
            type: "POST",
            url: `/forum/${forumId}/edit_post/${postId}/`,
            data: {
                'message': newMessage,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                $postCard.find('.post-display').removeClass('editing');
                $postCard.find('.edit-mode').removeClass('active');
                displayPosts();
                console.log("Post edited successfully!");
            },
            error: function (xhr, status, error) {
                alert("Error editing post.");
                
                $postCard.find('.post-display').removeClass('editing');
                $postCard.find('.edit-mode').removeClass('active');
            }
        });
    }

    // Delete Post Function
    function deletePost(postId) {
        $.ajax({
            type: "POST",
            url: `/forum/${forumId}/delete_post/${postId}/`,
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()  // Menghapus forum id dan post id dari data
            },
            success: function (data) {
                displayPosts();
            },
            error: function (xhr, status, error) {
                alert("Error deleting post.");
            }
        });
    }

    // **DISPLAY POSTS**
    function displayPosts() {
        $.ajax({
            url: `/forum/${forumId}/get_posts/`,
            type: "GET",
            success: function(response) {
                $('#postsContainer').empty();
                
                if (response.posts && response.posts.length > 0) {
                    response.posts.forEach(function(post) {
                        let deleteButton = '';
                        let editButton = '';
                        
                        if (response.user_is_authenticated && response.user_id == post.author_id) {
                            deleteButton = `<button class="btn btn-danger btn-sm delete-post" data-post-id="${post.id}">Delete</button>`;
                            editButton = `<button class="btn btn-secondary btn-sm edit-post" data-post-id="${post.id}">Edit</button>`;
                        }

                        if (post.is_edited) { 
                            post_info = `<div class="match-info">Posted on ${post.created_at}</div>`;
                        } else {
                            post_info = `<div class="match-info">Edited at ${post.created_at}</div>`;
                        }

                        var postHtml = `
                            <div class="match-card">
                                <div class="profile-post">
                                    <img src="${post.author_picture || defaultProfilePic}" alt="User Picture">
                                </div>

                                <div class="score-section">
                                    <!-- DISPLAY MODE -->
                                    <div class="post-display">
                                        <div class="post-authorname">${post.author_name}</div>
                                        <div class="score">${post.message}</div>
                                        ${post_info}
                                        <div class="post-actions">
                                            ${editButton}
                                            ${deleteButton}
                                        </div>
                                    </div>
                                    
                                    <!-- EDIT MODE -->
                                    <div class="edit-mode">
                                        <form class="edit-form">
                                            <textarea rows="3">${post.message}</textarea>
                                            <div class="edit-actions">
                                                <button type="button" class="btn btn-success btn-sm save-edit" data-post-id="${post.id}" id='save-button'>Save</button>
                                                <button type="button" class="btn btn-secondary btn-sm cancel-edit">Cancel</button>
                                            </div>
                                        </form>
                                    </div>
                            </div>
                        `;
                        $('#postsContainer').append(postHtml);
                    });
                } else {
                    $('#postsContainer').html('<p>No posts yet.</p>');
                }
            },
            error: function(xhr, status, error) {
                $('#postsContainer').html('<p>Error loading posts.</p>');
            }
        });
    }
});