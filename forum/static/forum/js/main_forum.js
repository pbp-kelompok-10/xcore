$(document).ready(function () {
    displayPosts();

    // ========================================
    // FILTER CONTROLS
    // ========================================

    // Apply Filters Button
    $("#applyFilters").on('click', function() {
        displayPosts();
    });

    // Reset Filters Button
    $("#resetFilters").on('click', function() {
        $("#searchInput").val('');
        $("#authorFilter").val('all');
        $("#sortSelect").val('newest');
        displayPosts();
    });

    // Enter key untuk search
    $("#searchInput").on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            displayPosts();
        }
    });

    // Sort/Filter select change - auto apply
    $("#sortSelect, #authorFilter").on('change', function() {
        displayPosts();
    });

    // ========================================
    // POST FORM
    // ========================================

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
                $("#postContent").val('');
                displayPosts();
                showToast('Success!', 'Your post has been added to the forum.', 'success');
            },
            error: function (xhr, status, error) {
                let errorMessage = 'Error sending post.';

                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }

                showToast('Failed!', errorMessage, 'error');
                $("#postContent").val('');
            }
        });
    });

    // ========================================
    // EDIT POST
    // ========================================

    // Edit Post Trigger
    $(document).on('click', '.edit-post', function(e) {
        e.preventDefault();
        let postId = $(this).data('post-id');
        let $postCard = $(this).closest('.match-card');
        
        // Close all other edit modes
        $('.edit-mode').removeClass('active');
        $('.post-display').removeClass('editing');
        
        // Toggle this post's edit mode
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

    // ========================================
    // DELETE POST
    // ========================================

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

    // ========================================
    // HELPER FUNCTIONS
    // ========================================

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
        // Ambil nilai filter
        const searchQuery = $("#searchInput").val().trim();
        const authorFilter = $("#authorFilter").val();
        const sortBy = $("#sortSelect").val();

        // Build query parameters
        let queryParams = {};
        if (searchQuery) queryParams.search = searchQuery;
        if (authorFilter) queryParams.author_filter = authorFilter;
        if (sortBy) queryParams.sort = sortBy;

        $.ajax({
            url: `/forum/${forumId}/get_posts/`,
            type: "GET",
            data: queryParams,
            success: function(response) {
                $('#postsContainer').empty();
                
                // ========================================
                // UPDATE RESULTS INFO
                // ========================================
                const activeFilters = [];
                if (searchQuery) activeFilters.push(`Search: "${searchQuery}"`);
                if (authorFilter === 'my_posts') activeFilters.push(`Filter: My Posts`);
                if (sortBy !== 'newest') {
                    const sortLabel = sortBy === 'oldest' ? 'Oldest First' : 'Recently Edited';
                    activeFilters.push(`Sort: ${sortLabel}`);
                }

                if (activeFilters.length > 0 || authorFilter === 'my_posts') {
                    $("#resultsInfo").html(
                        `📊 ${response.posts.length} post(s) found` + 
                        (activeFilters.length > 0 ? ` | ${activeFilters.join(' • ')}` : '')
                    ).show();
                } else {
                    $("#resultsInfo").hide();
                }

                // ========================================
                // RENDER POSTS
                // ========================================
                if (response.posts && response.posts.length > 0) {
                    response.posts.forEach(function(post) {
                        let deleteButton = '';
                        let editButton = '';
                        
                        if (response.user_is_authenticated) {
                            // Admin bisa delete semua post
                            if (response.user_is_admin) {
                                deleteButton = `<button class="btn btn-danger btn-sm delete-post" data-post-id="${post.id}">Delete</button>`;
                            }
                            
                            // User (termasuk admin) bisa edit dan delete post mereka sendiri
                            if (response.user_id == post.author_id) {
                                editButton = `<button class="btn btn-secondary btn-sm edit-post" data-post-id="${post.id}">Edit</button>`;
                                // Hanya tambahkan delete button jika belum ada dari kondisi admin
                                if (!deleteButton) {
                                    deleteButton = `<button class="btn btn-danger btn-sm delete-post" data-post-id="${post.id}">Delete</button>`;
                                }
                            }
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
                    // ========================================
                    // NO POSTS MESSAGE
                    // ========================================
                    let noResultsMsg = '<p>No posts yet. Be the first to post!</p>';
                    if (authorFilter === 'my_posts') {
                        noResultsMsg = '<p>You haven\'t posted anything yet.</p>';
                    } else if (searchQuery) {
                        noResultsMsg = '<p>No posts found matching your criteria. Try adjusting your filters.</p>';
                    }
                    $('#postsContainer').html(noResultsMsg);
                }
            },
            error: function(xhr, status, error) {
                $('#postsContainer').html('<p>Error loading posts.</p>');
                $("#resultsInfo").hide();
            }
        });
    }
});