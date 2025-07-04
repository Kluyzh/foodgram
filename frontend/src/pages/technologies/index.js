import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии проекта</h1>
      <div className={styles.content}>
        
        <div className={styles.section}>
          <h2 className={styles.sectionHeader}>Бекенд</h2>
          <div className={styles.text}>
            <ul className={styles.list}>
              <li className={styles.listItem}>Python 3.9</li>
              <li className={styles.listItem}>Django 4.2.22</li>
              <li className={styles.listItem}>Django REST Framework 3.16.0</li>
              <li className={styles.listItem}>Djoser 2.3.1 (аутентификация)</li>
              <li className={styles.listItem}>PostgreSQL 13 (база данных)</li>
              <li className={styles.listItem}>Gunicorn 23.0.0 (веб-сервер)</li>
              <li className={styles.listItem}>Psycopg2 2.9.9 (драйвер PostgreSQL)</li>
              <li className={styles.listItem}>Pillow 11.2.1 (обработка изображений)</li>
              <li className={styles.listItem}>Django-filter 25.1 (фильтрация данных)</li>
              <li className={styles.listItem}>Nginx 1.19 (прокси-сервер)</li>
            </ul>
          </div>
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionHeader}>Фронтенд</h2>
          <div className={styles.text}>
            <ul className={styles.list}>
              <li className={styles.listItem}>React</li>
            </ul>
          </div>
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionHeader}>Инфраструктура</h2>
          <div className={styles.text}>
            <ul className={styles.list}>
              <li className={styles.listItem}>Docker</li>
              <li className={styles.listItem}>Docker Compose</li>
            </ul>
          </div>
        </div>
        
      </div>
    </Container>
  </Main>
}

export default Technologies

