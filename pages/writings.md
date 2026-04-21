---
layout: default
title: "📚 글쓰기 공간"
permalink: /writings/
---

# 📚 글쓰기 공간

최승환의 생각과 연구를 기록하는 공간입니다. 박사논문부터 일상의 인사이트까지, 다양한 주제로 글을 작성합니다.

## 📅 최근 글들

<div id="recent-posts" class="posts-list">
  <!-- 최근 글 목록이 여기에 자동 생성됩니다 -->
</div>div>

## 📂 주제별 글 모음

<div class="topics-grid">
  {% for topic in site.data.writing_topics %}
      {% assign topic_posts = site.posts | where: "category", topic.id | sort: "date" | reverse %}
          <div class="topic-card" style="border-left: 4px solid {{ topic.color }}">
                <h3>{{ topic.title }}</h3>h3>
                <p class="topic-description">{{ topic.description }}</p>p>
                <p class="post-count">📝 {{ topic_posts | size }}개 글</p>p>
                {% if topic_posts.size > 0 %}
                  <ul class="topic-posts">
                              {% for post in topic_posts limit: 3 %}
                                <li><a href="{{ post.url }}">{{ post.title }}</a>a></li>li>
                            {% endfor %}
                  </ul>ul>
                  <a href="#topic-{{ topic.id }}" class="view-all">전체 보기 →</a>a>
                {% else %}
                  <p class="no-posts">아직 글이 없습니다.</p>p>
                {% endif %}
          </div>div>
  {% endfor %}
</div>div>

## 🔍 검색하기

<input type="text" id="search-input" placeholder="제목, 내용, 태그로 검색..." style="width: 100%; padding: 10px; margin: 20px 0;">
<div id="search-results"></div>div>

<style>
  .topics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin: 30px 0;
  }

  .topic-card {
        padding: 20px;
        border-radius: 8px;
        background: #f9f9f9;
        transition: all 0.3s;
        border: 1px solid #e0e0e0;
  }

  .topic-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
  }

  .topic-card h3 {
        margin: 0 0 10px 0;
        color: #333;
  }

  .topic-description {
        font-size: 14px;
        color: #666;
        margin: 8px 0;
  }

  .post-count {
        font-weight: bold;
        color: #2563eb;
        margin: 10px 0;
  }

  .topic-posts {
        list-style: none;
        padding: 0;
        margin: 10px 0;
  }

  .topic-posts li {
        padding: 5px 0;
        border-bottom: 1px solid #e0e0e0;
  }

  .topic-posts a {
        color: #2563eb;
        text-decoration: none;
  }

  .topic-posts a:hover {
        text-decoration: underline;
  }

  .view-all {
        color: #2563eb;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
  }

  .view-all:hover {
        text-decoration: underline;
  }

  .no-posts {
        color: #999;
        font-style: italic;
  }

  .posts-list {
        margin: 20px 0;
  }

  .post-item {
        padding: 15px;
        margin: 10px 0;
        background: white;
        border-left: 4px solid #2563eb;
        border-radius: 4px;
  }

  .post-title {
        font-weight: bold;
        margin: 0 0 5px 0;
  }

  .post-meta {
        font-size: 12px;
        color: #666;
  }
</style></li>
                  </h3>
