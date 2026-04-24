---
layout: default
title: "📚 글쓰기 공간"
permalink: /writings/
---

<style>
   .writings-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
   }

   .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding: 0 20px;
   }

   .calendar-header h2 {
        margin: 0;
        font-size: 24px;
   }

   .calendar-nav {
        display: flex;
        gap: 10px;
   }

   .calendar-nav button {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        padding: 8px 12px;
        cursor: pointer;
        border-radius: 4px;
        font-size: 14px;
   }

   .calendar-nav button:hover {
        background-color: #e0e0e0;
   }

   .calendar {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 1px;
        margin-bottom: 40px;
        background-color: #ddd;
        padding: 1px;
   }

   .calendar-day-header {
        background-color: #f9f9f9;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 12px;
   }

   .calendar-day {
        background-color: white;
        padding: 10px;
        min-height: 80px;
        position: relative;
        cursor: pointer;
        transition: background-color 0.2s;
   }

   .calendar-day:hover {
        background-color: #f0f0f0;
   }

   .calendar-day.other-month {
        background-color: #f9f9f9;
        color: #999;
   }

   .calendar-day.has-posts {
        background-color: #e3f2fd;
   }

   .calendar-day.has-posts::after {
        content: '';
        position: absolute;
        top: 5px;
        right: 5px;
        width: 8px;
        height: 8px;
        background-color: #2563eb;
        border-radius: 50%;
   }

   .calendar-day-number {
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 5px;
   }

   .calendar-day.other-month .calendar-day-number {
        color: #999;
   }

   .topic-card {
        background-color: white;
        border-left: 4px solid #2563eb;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
   }

   .topic-card.dissertation {
        border-left-color: #2563eb;
   }

   .topic-card.policy {
        border-left-color: #059669;
   }

   .topic-card.local-tax {
        border-left-color: #dc2626;
   }

   .topic-card.finance {
        border-left-color: #f59e0b;
   }

   .topic-card.daily-insight {
        border-left-color: #8b5cf6;
   }

   .topic-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
   }

   .topic-description {
        font-size: 13px;
        color: #666;
        margin-bottom: 10px;
   }

   .posts-section {
        margin-top: 40px;
   }

   .posts-section h3 {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #eee;
   }

   .post-item {
        background-color: white;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 4px;
        border-left: 3px solid #2563eb;
   }

   .post-date {
        font-size: 12px;
        color: #999;
        margin-right: 10px;
   }

   .post-title {
        font-weight: 500;
        color: #333;
   }

   .post-title:hover {
        color: #2563eb;
   }

   .tag {
        display: inline-block;
        background-color: #f0f0f0;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin-right: 5px;
        margin-top: 8px;
   }
 </style>

 <div class="writings-container">
    <div class="calendar-header">
         <h2 id="monthYear"></h2>h2>
         <div class="calendar-nav">
                <button onclick="previousMonth()">← 이전달</button>button>
                <button onclick="goToToday()">오늘</button>button>
                <button onclick="nextMonth()">다음달 →</button>button>
         </div>div>
    </div>div>

      <div class="calendar" id="calendar"></div>

          <div class="posts-section">
              <h3>주제별 글 모음</h3>
                  <div id="topicsContainer"></div>
                    </div>

                        <div class="posts-section">
                            <h3 id="selectedDateTitle">전체 글</h3>
                                <div id="postsContainer"></div>
                                  </div>
                                  </div>

                                  <script>
                                  let currentDate = new Date();
                                  let allPosts = [];

                                  // Jekyll site.posts 데이터 로드
                                  function initializePosts() {
                                    {% for post in site.posts %}
                                        allPosts.push({
                                              title: "{{ post.title }}",
                                                    url: "{{ post.url }}",
                                                          date: new Date("{{ post.date | date: '%Y-%m-%d' }}"),
                                                                category: "{{ post.categories[0] | default: 'daily-insight' }}",
                                                                      tags: [{% for tag in post.tags %}"{{ tag }}"{% if forloop.last == false %},{% endif %}{% endfor %}]
                                                                          });
                                                                            {% endfor %}
                                                                            }

                                                                            function renderCalendar() {
                                                                              const year = currentDate.getFullYear();
                                                                                const month = currentDate.getMonth();

                                                                                    document.getElementById('monthYear').textContent = year + '년 ' + (month + 1) + '월';

                                                                                        const firstDay = new Date(year, month, 1);
                                                                                          const lastDay = new Date(year, month + 1, 0);
                                                                                            const prevLastDay = new Date(year, month, 0);

                                                                                                const firstDayOfWeek = firstDay.getDay();
                                                                                                  const lastDate = lastDay.getDate();
                                                                                                    const prevLastDate = prevLastDay.getDate();
                                                                                                      
                                                                                                        const calendarDays = ['일', '월', '화', '수', '목', '금', '토'];
                                                                                                          let html = '';
                                                                                                            
                                                                                                              // 요일 헤더
                                                                                                                calendarDays.forEach(day => {
                                                                                                                    html += `<div class="calendar-day-header">${day}</div>`;
                                                                                                                      });
                                                                                                                        
                                                                                                                          // 이전달 날짜
                                                                                                                            for (let i = firstDayOfWeek - 1; i >= 0; i--) {
                                                                                                                                html += `<div class="calendar-day other-month"><div class="calendar-day-number">${prevLastDate - i}</div></div>`;
                                                                                                                                  }
                                                                                                                                    
                                                                                                                                      // 현재달 날짜
                                                                                                                                        for (let date = 1; date <= lastDate; date++) {
                                                                                                                                            const currentDateStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(date).padStart(2, '0');
                                                                                                                                                const postsForDate = allPosts.filter(post => {
                                                                                                                                                      const postDateStr = post.date.getFullYear() + '-' + 
                                                                                                                                                                                String(post.date.getMonth() + 1).padStart(2, '0') + '-' + 
                                                                                                                                                                                                          String(post.date.getDate()).padStart(2, '0');
                                                                                                                                                                                                                return postDateStr === currentDateStr;
                                                                                                                                                                                                                    });
                                                                                                                                                                                                                        
                                                                                                                                                                                                                            const hasPost = postsForDate.length > 0 ? ' has-posts' : '';
                                                                                                                                                                                                                                html += `<div class="calendar-day${hasPost}" onclick="selectDate(${date})"><div class="calendar-day-number">${date}</div></div>`;
                                                                                                                                                                                                                                  }
                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                      // 다음달 날짜
                                                                                                                                                                                                                                        const remainingDays = 42 - (firstDayOfWeek + lastDate);
                                                                                                                                                                                                                                          for (let i = 1; i <= remainingDays; i++) {
                                                                                                                                                                                                                                              html += `<div class="calendar-day other-month"><div class="calendar-day-number">${i}</div></div>`;
                                                                                                                                                                                                                                                }
                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                    document.getElementById('calendar').innerHTML = html;
                                                                                                                                                                                                                                                      renderTopics();
                                                                                                                                                                                                                                                      }
                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                      function renderTopics() {
                                                                                                                                                                                                                                                        const topics = [
                                                                                                                                                                                                                                                            { id: 'dissertation', title: '박사논문', color: '#2563eb' },
                                                                                                                                                                                                                                                                { id: 'policy', title: '정책 & 자문', color: '#059669' },
                                                                                                                                                                                                                                                                    { id: 'local-tax', title: '지방세 연구', color: '#dc2626' },
                                                                                                                                                                                                                                                                        { id: 'finance', title: '재무설계', color: '#f59e0b' },
                                                                                                                                                                                                                                                                            { id: 'daily-insight', title: '일상 & 인사이트', color: '#8b5cf6' }
                                                                                                                                                                                                                                                                              ];
                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                  let html = '';
                                                                                                                                                                                                                                                                                    topics.forEach(topic => {
                                                                                                                                                                                                                                                                                        const postsForTopic = allPosts.filter(p => p.category === topic.id).slice(0, 3);
                                                                                                                                                                                                                                                                                            html += `<div class="topic-card ${topic.id}">
                                                                                                                                                                                                                                                                                                          <div class="topic-title">${topic.title}</div>
                                                                                                                                                                                                                                                                                                                        <div class="topic-description">최신 글 ${postsForTopic.length}개</div>`;
                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                if (postsForTopic.length > 0) {
                                                                                                                                                                                                                                                                                                                                      postsForTopic.forEach(post => {
                                                                                                                                                                                                                                                                                                                                              html += `<div class="post-item"><a href="${post.url}" class="post-title">${post.title}</a></div>`;
                                                                                                                                                                                                                                                                                                                                                    });
                                                                                                                                                                                                                                                                                                                                                        } else {
                                                                                                                                                                                                                                                                                                                                                              html += '<div style="color: #999; font-size: 12px;">아직 작성된 글이 없습니다.</div>';
                                                                                                                                                                                                                                                                                                                                                                  }
                                                                                                                                                                                                                                                                                                                                                                      html += '</div>';
                                                                                                                                                                                                                                                                                                                                                                        });
                                                                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                                                                            document.getElementById('topicsContainer').innerHTML = html;
                                                                                                                                                                                                                                                                                                                                                                            }
                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                            function selectDate(date) {
                                                                                                                                                                                                                                                                                                                                                                              const dateStr = currentDate.getFullYear() + '-' + 
                                                                                                                                                                                                                                                                                                                                                                                                String(currentDate.getMonth() + 1).padStart(2, '0') + '-' + 
                                                                                                                                                                                                                                                                                                                                                                                                                  String(date).padStart(2, '0');
                                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                                                                      const postsForDate = allPosts.filter(post => {
                                                                                                                                                                                                                                                                                                                                                                                                                          const postDateStr = post.date.getFullYear() + '-' + 
                                                                                                                                                                                                                                                                                                                                                                                                                                                  String(post.date.getMonth() + 1).padStart(2, '0') + '-' + 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                          String(post.date.getDate()).padStart(2, '0');
                                                                                                                                                                                                                                                                                                                                                                                                                                                                              return postDateStr === dateStr;
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                });
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    document.getElementById('selectedDateTitle').textContent = dateStr + '의 글';
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        let html = '';
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          if (postsForDate.length > 0) {
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              postsForDate.forEach(post => {
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    html += `<div class="post-item">
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    <span class="post-date">${post.date.toLocaleDateString('ko-KR')}</span>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    <a href="${post.url}" class="post-title">${post.title}</a>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  </div>`;
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      });
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        } else {
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            html = '<p style="color: #999;">이 날짜에 작성된 글이 없습니다.</p>';
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  document.getElementById('postsContainer').innerHTML = html;
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  function previousMonth() {
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    currentDate.setMonth(currentDate.getMonth() - 1);
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      renderCalendar();
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      function nextMonth() {
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        currentDate.setMonth(currentDate.getMonth() + 1);
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          renderCalendar();
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          function goToToday() {
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            currentDate = new Date();
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              renderCalendar();
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              // 초기화
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              initializePosts();
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              renderCalendar();
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              </script>
</style>
