# Highlights CRUD Operations Documentation

## Overview
Complete Create, Read, Update, and Delete (CRUD) operations for the Highlights feature with superuser-only access for create/update/delete operations.

---

## Views (highlights/views.py)

### READ OPERATIONS

#### 1. `highlight_test(request)`
- **Purpose**: Test endpoint to display sample highlights
- **Access**: Public
- **Response**: Renders test highlight with Portugal vs Belgium match
- **URL**: `/highlights/test/`

#### 2. `highlight_detail(request, match_id)`
- **Purpose**: Retrieve and display a specific highlight by match ID
- **Access**: Public
- **Parameters**: `match_id` (UUID)
- **Response**: Renders highlight.html with match info and video
- **URLs**: 
  - `/highlights/<uuid>/`
  - `/match/<uuid>/highlights/`

#### 3. `highlight_list(request)`
- **Purpose**: List all highlights
- **Access**: Public
- **Response**: Renders table of all highlights with actions
- **URL**: `/highlights/`

---

### CREATE OPERATIONS

#### 4. `highlight_create(request, match_id)`
- **Purpose**: Create a new highlight for a specific match
- **Access**: **Superuser only** (returns 403 Forbidden otherwise)
- **Parameters**: `match_id` (UUID)
- **Methods**: GET (show form), POST (save highlight)
- **Features**:
  - Prevents duplicate highlights for same match
  - Auto-assigns match
  - Redirects to highlight_detail on success
- **URL**: `/highlights/create/<uuid>/`

---

### UPDATE OPERATIONS

#### 5. `highlight_update(request, match_id)`
- **Purpose**: Update an existing highlight
- **Access**: **Superuser only** (returns 403 Forbidden otherwise)
- **Parameters**: `match_id` (UUID)
- **Methods**: GET (show form with current data), POST (save changes)
- **Features**:
  - Pre-fills form with existing highlight data
  - Shows match info in read-only mode
- **URL**: `/highlights/update/<uuid>/`

---

### DELETE OPERATIONS

#### 6. `highlight_delete(request, match_id)`
- **Purpose**: Delete a highlight
- **Access**: **Superuser only** (returns 403 Forbidden otherwise)
- **Parameters**: `match_id` (UUID)
- **Methods**: POST only
- **Response**: Redirects to highlight_list
- **URL**: `/highlights/delete/<uuid>/`

---

### LEGACY

#### 7. `add_highlight(request, match_id=None)`
- **Purpose**: Legacy function (use `highlight_create` instead)
- **Access**: Superuser only
- **Note**: Kept for backward compatibility

---

## URL Patterns (highlights/urls.py)

```python
# Read Operations
/highlights/test/                          → highlight_test
/highlights/                               → highlight_list
/highlights/<uuid>/                        → highlight_detail
/match/<uuid>/highlights/                  → highlight_detail

# Create Operation
/highlights/create/<uuid>/                 → highlight_create

# Update Operation
/highlights/update/<uuid>/                 → highlight_update

# Delete Operation
/highlights/delete/<uuid>/                 → highlight_delete

# Legacy
/highlights/add/                           → add_highlight
/highlights/add/<uuid>/                    → add_highlight
```

---

## Forms (highlights/forms.py)

### HighlightForm

**Fields**:
- `match`: Select dropdown of available matches (required for create)
- `video`: URL input for embed video URL (required)

**Widgets**:
- Bootstrap-style form controls with custom styling
- Placeholder text guiding users to YouTube/Vimeo embed URLs

---

## Templates

### 1. highlight_form.html
**Purpose**: Form for creating/updating highlights

**Context Variables**:
- `form`: HighlightForm instance
- `match`: Match object
- `action`: "Create" or "Update"

**Features**:
- Responsive form layout
- Error message display
- Match info in read-only mode for updates
- Cancel button linking back to highlight detail

### 2. highlight_list.html
**Purpose**: Display all highlights in table format

**Context Variables**:
- `highlights`: QuerySet of all Highlight objects with related matches

**Features**:
- Responsive table with match info and score
- View, Edit, Delete action buttons (edit/delete superuser only)
- Empty state when no highlights exist
- Confirmation dialog for deletion

---

## Security Features

### Superuser Protection
```python
if not request.user.is_superuser:
    return HttpResponseForbidden("You do not have permission...")
```

All Create, Update, and Delete operations check for superuser status before proceeding.

### Login Required
All CRUD operations (except list and detail views) require user to be logged in via `@login_required` decorator.

### CSRF Protection
All forms include `{% csrf_token %}` for CSRF security.

---

## Usage Examples

### Create a Highlight
```
GET  /highlights/create/123e4567-e89b-12d3-a456-426614174000/
POST /highlights/create/123e4567-e89b-12d3-a456-426614174000/
```

### Update a Highlight
```
GET  /highlights/update/123e4567-e89b-12d3-a456-426614174000/
POST /highlights/update/123e4567-e89b-12d3-a456-426614174000/
```

### Delete a Highlight
```
POST /highlights/delete/123e4567-e89b-12d3-a456-426614174000/
```

### View Highlight
```
GET /match/123e4567-e89b-12d3-a456-426614174000/highlights/
```

### List All Highlights
```
GET /highlights/
```

---

## Database Considerations

- Highlights use `OneToOneField` to Match (one highlight per match)
- `match_id` is a UUID field
- EmbedVideoField stores video URL for embedding

---

## Error Handling

| Scenario | Response |
|----------|----------|
| Non-superuser attempts create/update/delete | 403 Forbidden |
| User not logged in | Redirects to login |
| Match not found | 404 Not Found |
| Highlight not found | 404 Not Found |
| Form validation fails | Re-renders form with errors |

---

## Future Enhancements

- [ ] Add pagination to highlight_list
- [ ] Add search/filter functionality
- [ ] Add bulk actions
- [ ] Add video preview/thumbnail
- [ ] Add timestamp for when highlight was created
- [ ] Add soft delete (archive) instead of permanent delete
