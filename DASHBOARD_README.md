# 🌸 SheSpeaks Pulse

A modern, interactive pulse dashboard for analyzing responses from the SheSpeaks 2025 survey. Built with Streamlit and designed with a Gen Z aesthetic.

## ✨ Features

### 🏠 Overview Page
- **Key Metrics Cards**: Total responses, weekly activity, demographics, and bias indicators
- **Response Timeline**: Daily response rate visualization
- **Recent Activity Feed**: Latest submissions
- **Quick Actions**: Download CSV, export reports, refresh data

### 📊 Demographics Page
- **Year Distribution**: Interactive pie chart showing year-wise breakdown
- **Course Analysis**: Horizontal bar chart of top courses
- **Response Timeline**: Area chart showing submission patterns over time

### 🎭 Experiences Page
- **Gender Bias Analysis**: "Felt judged?" responses visualization
- **Voice in Groups**: How students feel their voices are heard
- **Stepped Back Analysis**: Patterns of stepping back from tech activities
- **Correlation Matrix**: Relationships between different experiences

### 🏗️ Infrastructure Page
- **Curfew Impact**: How hostel curfews affect tech participation
- **Support Systems**: Comparison of "equal chances" vs "safe and supported"
- **Boys' Club Perception**: Distribution of responses about engineering culture

### 💭 Insights Page
- **5-Point Scale Analysis**: Radar chart of sentiment questions
- **What Would Help**: Analysis of requested improvements
- **Deep Analytics**: Sentiment analysis and categorized responses

### 📈 Trends Page
- **Time-based Analysis**: Weekly and daily response patterns
- **Year-wise Comparison**: Comparative studies across different years
- **Predictive Trends**: Pattern analysis and anomaly detection

## 🎨 Design Features

- **Modern Gen Z Aesthetic**: Pink/purple gradient theme
- **Glassmorphism Design**: Frosted glass effects and blur
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Charts**: Hover effects and click interactions
- **Smooth Animations**: Hover effects and transitions

## 🚀 Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_dashboard.txt
   ```

2. **Setup Firebase**:
   - Ensure `firebase_key.json` is in the project directory
   - Or set up environment variables for Firebase authentication

3. **Run the Dashboard**:
   ```bash
   streamlit run app.py
   ```

## 📱 Usage

1. **Navigation**: Use the navbar to switch between different analysis pages
2. **Interactions**: Hover over charts for detailed information
3. **Downloads**: Use quick action buttons to export data
4. **Filters**: Apply date ranges and other filters (coming soon)

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Charts**: Plotly (interactive visualizations)
- **Data Processing**: Pandas, NumPy
- **Backend**: Firebase Firestore
- **Styling**: Custom CSS with modern design principles

## 🎯 Key Metrics Tracked

- **Response Volume**: Total submissions and trends
- **Demographics**: Year and course distribution
- **Experiences**: Gender bias and discrimination patterns
- **Infrastructure**: Support systems and resource availability
- **Sentiment**: 5-point scale question analysis
- **Trends**: Time-based patterns and correlations

## 🔮 Future Enhancements

- **Real-time Updates**: Live data refresh
- **Advanced Filters**: Date ranges, demographics, etc.
- **Export Features**: PDF reports, PowerPoint presentations
- **Predictive Analytics**: Machine learning insights
- **Mobile App**: Native mobile application
- **API Integration**: RESTful API for external access

## 🎨 Color Scheme

- **Primary**: `#ff9a9e` (Soft Pink)
- **Secondary**: `#fecfef` (Light Pink)
- **Background**: `#f5f7fa` to `#c3cfe2` (Gradient)
- **Text**: `#333` (Dark Gray)
- **Accent**: `#666` (Medium Gray)

## 📊 Data Sources

The dashboard pulls data from Firebase Firestore collection "responses" with the following structure:
- Basic demographics (year, course)
- Experience questions (judged, voice, stepped-back)
- Infrastructure questions (curfews, support systems)
- 5-point scale questions (boys-club, equal-chances, etc.)
- Text responses (held-back-report, one-change, advice)
- Timestamps and metadata

---

*Built with ❤️ for women in tech*
