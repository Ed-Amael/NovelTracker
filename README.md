# Novel Tracker

A clean, modern web application for tracking your novel reading progress. Built with Flask, SQLite, and modern CSS - perfect for both local development and Vercel deployment.

## Features

- **User Authentication**: Secure registration and login system
- **Novel Search**: Find novels by title, author, or tags
- **Reading Lists**: Track novels with statuses (Want to Read, Reading, Completed, Dropped, On Hold)
- **Ratings & Reviews**: 5-star rating system with optional reviews
- **Modern UI**: Beautiful, responsive design with dark/light mode toggle
- **Mobile Friendly**: Works perfectly on all devices
- **Zero Build**: No npm/Node.js required - pure Python and web standards

## Tech Stack

- **Backend**: Python 3.12 + Flask 3.0
- **Database**: SQLite (file-based)
- **Frontend**: HTML5 + Modern CSS + Vanilla JavaScript
- **Authentication**: Flask-Login + Werkzeug security
- **Deployment**: Vercel (serverless functions)

## Quick Start

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <your-repo-url>
   cd "Novel Tracker"
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

The app will automatically create a SQLite database with sample novels on first run.

### Vercel Deployment

#### One-Click Deploy (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/novel-tracker)

#### Manual Deployment

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/novel-tracker.git
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project" → "Import Git Repository"
   - Select your repository
   - Vercel will auto-detect Python and use the `vercel.json` configuration
   - Click "Deploy"

3. **Environment Variables (Optional):**
   - Add `SECRET_KEY` for production security
   - Go to Project Settings → Environment Variables

## ⚠️ Important: Database Persistence

**On Vercel free tier, SQLite is ephemeral** - your data will be lost on each redeploy. For persistent data, consider:

- **Turso/libSQL** - SQLite-compatible serverless database
- **Neon Postgres** - Serverless PostgreSQL
- **Supabase** - PostgreSQL with real-time features
- **Upstash Redis + KV** - For simple key-value storage

For local development and demos, SQLite works perfectly.

## Project Structure

```
Novel Tracker/
├── app.py                  # Main Flask application
├── vercel.json             # Vercel configuration
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version
├── data/
│   └── novels.db           # SQLite database (auto-created)
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── login.html          # Login form
│   ├── register.html       # Registration form
│   ├── search.html         # Novel search
│   ├── novel.html          # Novel details
│   └── mylist.html         # User's reading list
├── static/
│   ├── css/
│   │   └── style.css       # Modern CSS with dark/light mode
│   ├── js/
│   │   └── theme.js        # Theme toggle and interactions
│   └── images/             # Novel covers (optional)
└── README.md               # This file
```

## Database Schema

### Users
- `id` (Primary Key)
- `email` (Unique)
- `password_hash`
- `created_at`

### Novels
- `id` (Primary Key)
- `title`
- `author`
- `synopsis`
- `cover_image`
- `status` (Ongoing/Completed/Hiatus)
- `total_chapters`
- `tags` (Comma-separated)

### Reading Lists
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `novel_id` (Foreign Key)
- `status` (Want to Read/Reading/Completed/Dropped/On Hold)
- `rating` (1-5 stars)
- `review` (Optional text)
- `created_at`
- `updated_at`

## Customization

### Adding Novels

The app includes sample data. To add more novels:

1. **Via Database:**
   ```python
   from app import Novel, db
   
   novel = Novel(
       title="Your Novel Title",
       author="Author Name",
       synopsis="Novel description...",
       status="Ongoing",
       total_chapters=100,
       tags="Action, Fantasy, Adventure"
   )
   db.session.add(novel)
   db.session.commit()
   ```

2. **Via Admin Panel:**
   - Create an admin route for CRUD operations
   - Add forms for novel management

### Styling

- Edit `static/css/style.css` for visual changes
- CSS variables in `:root` control colors and spacing
- Dark mode automatically handled via `[data-theme="dark"]`

### Features to Add

- **Chapter Progress**: Track current chapter per novel
- **Social Features**: Follow other users, see their lists
- **Recommendations**: Simple algorithm based on tags/ratings
- **API Endpoints**: REST API for mobile apps
- **Import/Export**: CSV or JSON data import/export

## Security Notes

- Passwords are hashed using Werkzeug's `generate_password_hash`
- CSRF protection should be added for forms in production
- SQL injection prevented via SQLAlchemy ORM
- User input escaped in Jinja2 templates

## Development Tips

### Running Tests

```bash
# Install pytest
pip install pytest

# Run tests
pytest
```

### Code Quality

```bash
# Install linting tools
pip install flake8 black

# Format code
black .

# Check style
flake8 .
```

### Debug Mode

The app runs in debug mode by default. For production:

```python
app.run(debug=False)
```

## Troubleshooting

### Common Issues

1. **Database not found:**
   - Ensure `data/` directory exists
   - Run `python app.py` to auto-create database

2. **Vercel deployment fails:**
   - Check `runtime.txt` matches supported Python version
   - Verify `vercel.json` syntax
   - Check Vercel logs for specific errors

3. **Theme not persisting:**
   - Ensure localStorage is enabled in browser
   - Check browser console for JavaScript errors

4. **Static files not loading:**
   - Verify `static/` folder structure
   - Check Flask's `url_for()` usage in templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

- Create an issue on GitHub for bugs
- Check the troubleshooting section above
- Review Flask and Vercel documentation for platform-specific issues

---

**Happy Reading! 📚**