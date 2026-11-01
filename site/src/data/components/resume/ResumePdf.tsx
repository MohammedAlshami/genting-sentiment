import { Document, Page, Text, View, StyleSheet, Link } from '@react-pdf/renderer';
import {
  ACHIEVEMENTS,
  EDUCATION,
  EMAIL,
  EXPERIENCE,
  LOCATION,
  NAME,
  PORTFOLIO,
  PORTFOLIO_URL,
  PROJECTS,
  RESEARCH,
  SKILLS,
  TITLE,
} from '../../resume-data';

/** Harvard-style résumé: Times, centred header, ruled section headings, right-aligned dates. */
const S = StyleSheet.create({
  page: {
    paddingTop: 28,
    paddingBottom: 24,
    paddingHorizontal: 40,
    fontFamily: 'Times-Roman',
    fontSize: 9.6,
    lineHeight: 1.13,
    color: '#000000',
  },
  name: { fontFamily: 'Times-Bold', fontSize: 18, lineHeight: 1.15, textAlign: 'center', letterSpacing: 0.8 },
  contact: { textAlign: 'center', fontSize: 9.2, marginTop: 4 },
  tagline: { textAlign: 'center', fontFamily: 'Times-Italic', fontSize: 9.7, marginTop: 2 },
  link: { color: '#000000', textDecoration: 'none' },
  sectionTitle: {
    fontFamily: 'Times-Bold',
    fontSize: 10.2,
    marginTop: 7,
    marginBottom: 3.2,
    paddingBottom: 1.5,
    borderBottomWidth: 0.9,
    borderBottomColor: '#000000',
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  bold: { fontFamily: 'Times-Bold' },
  italic: { fontFamily: 'Times-Italic' },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  entry: { marginTop: 4.5 },
  firstEntry: { marginTop: 0 },
  bulletRow: { flexDirection: 'row', marginTop: 1.4 },
  bulletDot: { width: 11, paddingLeft: 2 },
  bulletText: { flex: 1 },
  skillRow: { flexDirection: 'row', marginTop: 1.6 },
  skillLabel: { fontFamily: 'Times-Bold', width: 82 },
  skillItems: { flex: 1 },
  achCol: { width: '50%' },
});

export function ResumePdf() {
  const half = Math.ceil(ACHIEVEMENTS.length / 2);
  return (
    <Document title={`${NAME} — Résumé`} author={NAME} subject={TITLE}>
      <Page size="LETTER" style={S.page}>
        {/* Header */}
        <Text style={S.name}>{NAME.toUpperCase()}</Text>
        <Text style={S.contact}>
          {LOCATION} · {EMAIL} · <Link src={PORTFOLIO_URL} style={S.link}>{PORTFOLIO}</Link>
        </Text>
        <Text style={S.tagline}>{TITLE}</Text>

        {/* Education */}
        <Text style={S.sectionTitle}>Education</Text>
        <View style={S.row}>
          <Text style={S.bold}>{EDUCATION.school}</Text>
          <Text>{EDUCATION.period}</Text>
        </View>
        <Text style={S.italic}>{EDUCATION.degree}</Text>
        <Text>{EDUCATION.detail}</Text>

        {/* Experience */}
        <Text style={S.sectionTitle}>Experience</Text>
        {EXPERIENCE.map((job, idx) => (
          <View key={`${job.org}-${job.role}`} style={idx === 0 ? S.firstEntry : S.entry} wrap={false}>
            <View style={S.row}>
              <Text style={S.bold}>{job.org}</Text>
              <Text>{job.period}</Text>
            </View>
            <View style={S.row}>
              <Text style={S.italic}>{job.role}</Text>
              <Text style={S.italic}>{job.meta}</Text>
            </View>
            {job.points.map((point, i) => (
              <View key={i} style={S.bulletRow}>
                <Text style={S.bulletDot}>•</Text>
                <Text style={S.bulletText}>{point}</Text>
              </View>
            ))}
          </View>
        ))}

        {/* Projects */}
        <Text style={S.sectionTitle}>Projects</Text>
        {PROJECTS.map((p, idx) => (
          <View key={p.title} style={idx === 0 ? S.firstEntry : S.entry} wrap={false}>
            <Text>
              <Text style={S.bold}>{p.title}</Text>
              <Text style={S.italic}> — {p.tag}</Text>
              {p.repo && (
                <Text>
                  {' · '}
                  <Link src={p.repo.href} style={S.link}>
                    {p.repo.label}
                  </Link>
                </Text>
              )}
            </Text>
            {p.points.map((point, i) => (
              <View key={i} style={S.bulletRow}>
                <Text style={S.bulletDot}>•</Text>
                <Text style={S.bulletText}>{point}</Text>
              </View>
            ))}
          </View>
        ))}

        {/* Research */}
        <Text style={S.sectionTitle}>Research</Text>
        <Text>
          {RESEARCH.authors} <Text style={S.italic}>{RESEARCH.title}</Text> {RESEARCH.venue} {RESEARCH.doi}
        </Text>

        {/* Achievements */}
        <Text style={S.sectionTitle}>Achievements</Text>
        <View style={{ flexDirection: 'row' }}>
          <View style={S.achCol}>
            {ACHIEVEMENTS.slice(0, half).map((item) => (
              <Text key={item} style={{ marginTop: 1.4 }}>
                • {item}
              </Text>
            ))}
          </View>
          <View style={S.achCol}>
            {ACHIEVEMENTS.slice(half).map((item) => (
              <Text key={item} style={{ marginTop: 1.4 }}>
                • {item}
              </Text>
            ))}
          </View>
        </View>

        {/* Skills */}
        <Text style={S.sectionTitle}>Technical Skills</Text>
        {SKILLS.map((s) => (
          <View key={s.label} style={S.skillRow}>
            <Text style={S.skillLabel}>{s.label}:</Text>
            <Text style={S.skillItems}>{s.items}</Text>
          </View>
        ))}
      </Page>
    </Document>
  );
}
