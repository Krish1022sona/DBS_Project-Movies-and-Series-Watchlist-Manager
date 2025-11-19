# Guide for Replacing Fake URLs in reset_database.py

This guide explains how to replace the placeholder URLs in the `reset_database.py` script with real URLs for poster images and photos. This ensures the database contains valid, accessible image links for media posters and actor photos.

## Poster Images for Media

In the `media` list within the `insert_data()` function, the `poster_image_url` field currently contains fake placeholder URLs (e.g., `'https://example.com/sholay.jpg'`). These should be replaced with real poster image URLs.

### Where to Find Real URLs:
- **TMDB (The Movie Database) API**: Use the TMDB API to fetch poster paths. For example, search for a movie and get the `poster_path` from the response, then construct the full URL as `https://image.tmdb.org/t/p/w500/{poster_path}`.
- **IMDb or Other Databases**: Manually search on IMDb or similar sites and copy the poster image URL.
- **Free Image Sources**: Ensure the URLs point to publicly accessible images (e.g., from Wikimedia Commons or official movie sites).

### Example Replacement:
**Before:**
```python
('M001', 'Sholay', 'A classic Bollywood action drama about revenge and friendship.', 1975, 'Movie', 'U', 'https://example.com/sholay.jpg', 9.0),
```

**After:**
```python
('M001', 'Sholay', 'A classic Bollywood action drama about revenge and friendship.', 1975, 'Movie', 'U', 'https://image.tmdb.org/t/p/w500/abc123def.jpg', 9.0),
```

Replace all instances in the `media` list (around lines 300-400 in the script).

## Photo URLs for People

In the `people` list within the `insert_data()` function, the `photo_url` field contains fake placeholder URLs (e.g., `'https://example.com/bachchan.jpg'`). These should be replaced with real photo URLs of the actors.

### Where to Find Real URLs:
- **TMDB API**: Similar to posters, use TMDB to get profile images for people.
- **IMDb or Wikipedia**: Search for the actor's page and copy a suitable photo URL.
- **Free Image Sources**: Use high-quality, publicly accessible photos (ensure copyright compliance).

### Example Replacement:
**Before:**
```python
('P001', 'Amitabh Bachchan', date(1942, 10, 11), 'https://example.com/bachchan.jpg'),
```

**After:**
```python
('P001', 'Amitabh Bachchan', date(1942, 10, 11), 'https://image.tmdb.org/t/p/w500/def456ghi.jpg'),
```

Replace all instances in the `people` list (around lines 400-500 in the script).

## Important Notes:
- **Validity**: Test the URLs to ensure they load correctly and are not broken.
- **Copyright**: Use URLs from free or licensed sources to avoid legal issues.
- **Automation**: If possible, write a script to fetch URLs programmatically using APIs like TMDB to automate this process.
- **Backup**: Before making changes, back up the original `reset_database.py` file.

After replacing the URLs, re-run the `reset_database.py` script to update the database with the new links.
