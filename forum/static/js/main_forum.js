$(document).ready(function () {
    displayPosts();

    $("#postForm").on('submit', function(event) {
        event.preventDefault();
        let postContent = $("#postContent").val().trim();
        
        if (!postContent) {
            Swal.fire({
                icon: 'warning',
                title: 'Oops!',
                text: 'Please write something!',
            });
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
                if (!data.user_is_authenticated){
                    showToast('Gagal!', 'Kamu harus login untuk menambahkan postingan.');
                    $("#postContent").val('');
                    return;
                }

                $("#postContent").val('');
                displayPosts();
                showToast('Berhasil!', 'Postingan kamu sudah ditambahkan ke forum.');
            },
            error: function (xhr, status, error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error sending post.',
                });
            }
        });
    });

    // Edit Post Trigger
    $(document).on('click', '.edit-post', function(e) {
        e.preventDefault();
        let postId = $(this).data('post-id');
        let $postCard = $(this).closest('.match-card');
        
        $('.edit-mode').removeClass('active');
        $('.post-display').removeClass('editing');
        
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
            Swal.fire({
                icon: 'warning',
                title: 'Oops!',
                text: 'Message cannot be empty!',
            });
            return;
        }

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
        
        Swal.fire({
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
                showToast('Berhasil!', 'Postingan kamu sudah diperbarui.');
            },
            error: function (xhr, status, error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error editing post.',
                });
                $postCard.find('.post-display').removeClass('editing');
                $postCard.find('.edit-mode').removeClass('active');
            }
        });
    }

    function deletePost(postId) {
        $.ajax({
            type: "POST",
            url: `/forum/${forumId}/delete_post/${postId}/`,
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                displayPosts();
                showToast('Berhasil!', 'Postingan kamu sudah dihapus.');
            },
            error: function (xhr, status, error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error deleting post.',
                });
            }
        });
    }

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

                        let postInfo = '';
                        if (!post.is_edited) {
                            postInfo = `<div class="match-info">Posted on ${post.created_at}</div>`;
                        } else {
                            postInfo = `<div class="match-info">Edited at ${post.edited_at}</div>`;
                        }

                        let postHtml = `
                            <div class="match-card">
                                <div class="profile-post">
                                    <img src="${post.author_picture || defaultProfilePic}" alt="User Picture">
                                </div>
                                <div class="score-section">
                                    <div class="post-display">
                                        <div class="post-authorname">${post.author_name}</div>
                                        <div class="score">${post.message}</div>
                                        ${postInfo}
                                        <div class="post-actions">
                                            ${editButton}
                                            ${deleteButton}
                                        </div>
                                    </div>
                                    <div class="edit-mode">
                                        <form class="edit-form">
                                            <textarea rows="3">${post.message}</textarea>
                                            <div class="edit-actions">
                                                <button type="button" class="btn btn-success btn-sm save-edit" data-post-id="${post.id}">Save</button>
                                                <button type="button" class="btn btn-secondary btn-sm cancel-edit">Cancel</button>
                                            </div>
                                        </form>
                                    </div>
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