import React from 'react';
import { Link } from 'react-router-dom';
import '../../styles/pages/about/AboutPage.css';

const AboutPage = () => {
  return (
    <div className="about-page">
      <header className="about-header">
        <h1>About Me</h1>
        <p className="about-subtitle">Full-Stack Developer & Tournament Management System Creator</p>
      </header>

      <main className="about-content">
        {/* Personal Introduction */}
        <section className="about-section">
          <div className="profile-card">
            <div className="profile-image">
              <div className="profile-avatar">
                <span className="avatar-text">YK</span>
              </div>
            </div>
            <div className="profile-info">
              <h2>Yu Hung Kung</h2>
              <p className="profile-title">Full-Stack Developer</p>
              <p className="profile-location">Los Angeles, CA</p>
            </div>
          </div>
        </section>

        {/* About This Project */}
        <section className="about-section">
          <h2>About This Project</h2>
          <div className="project-description">
            <p>
              This Tournament Management System is a comprehensive full-stack web application 
              I developed to streamline sports tournament operations. The system features 
              real-time score updates, intelligent match scheduling, and role-based access control.
            </p>
            <p>
              Built with modern technologies including React.js, Flask, and WebSocket, 
              this project demonstrates my expertise in full-stack development, real-time 
              programming, and complex system architecture.
            </p>
          </div>
        </section>

        {/* Technical Skills */}
        <section className="about-section">
          <h2>Technical Skills</h2>
          <div className="skills-grid">
            <div className="skill-category">
              <h3>Frontend</h3>
              <div className="skill-tags">
                <span className="skill-tag">React.js</span>
                <span className="skill-tag">JavaScript</span>
                <span className="skill-tag">CSS3</span>
                <span className="skill-tag">HTML5</span>
                <span className="skill-tag">Socket.IO</span>
              </div>
            </div>
            <div className="skill-category">
              <h3>Backend</h3>
              <div className="skill-tags">
                <span className="skill-tag">Python</span>
                <span className="skill-tag">Flask</span>
                <span className="skill-tag">SQLAlchemy</span>
                <span className="skill-tag">JWT</span>
                <span className="skill-tag">WebSocket</span>
              </div>
            </div>
            <div className="skill-category">
              <h3>Database & Tools</h3>
              <div className="skill-tags">
                <span className="skill-tag">SQLite</span>
                <span className="skill-tag">Pandas</span>
                <span className="skill-tag">Excel Integration</span>
                <span className="skill-tag">Git</span>
                <span className="skill-tag">Deployment</span>
              </div>
            </div>
          </div>
        </section>

        {/* Key Features */}
        <section className="about-section">
          <h2>Key Features Implemented</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-time Updates</h3>
              <p>WebSocket-based live score synchronization across all users</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🧠</div>
              <h3>Intelligent Scheduling</h3>
              <p>Algorithm to prevent consecutive player conflicts and optimize court usage</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔐</div>
              <h3>Role-based Access</h3>
              <p>Granular permissions system for Admin, Host, Umpire, and User roles</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Data Integration</h3>
              <p>Excel/CSV upload system for tournament schedules and registration data</p>
            </div>
          </div>
        </section>

        {/* Contact & Links */}
        <section className="about-section">
          <h2>Get In Touch</h2>
          <div className="contact-info">
            <p>Interested in collaborating or have questions about this project?</p>
            <div className="contact-links">
              <a href="yuhungku@usc.edu" className="contact-link">
                📧 Email Me
              </a>
              <a href="https://github.com/alex1792" className="contact-link" target="_blank" rel="noopener noreferrer">
                💻 GitHub
              </a>
              <a href="https://www.linkedin.com/in/yu-hung-kung-9819b7233/" className="contact-link" target="_blank" rel="noopener noreferrer">
                💼 LinkedIn
              </a>
            </div>
          </div>
        </section>

        {/* Back to Home */}
        <section className="about-section">
          <div className="back-to-home">
            <Link to="/" className="back-button">
              ← Back to Tournament System
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
};

export default AboutPage;