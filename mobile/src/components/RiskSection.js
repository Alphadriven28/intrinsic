import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, BASE } from '../theme';

export default function RiskSection({ risk }) {
    if (!risk) return null;

    const level = risk.overall_risk || 'Unknown';
    const badgeStyle = level === 'Low' ? { bg: COLORS.greenBg, color: COLORS.greenDeep }
        : level === 'High' ? { bg: COLORS.redBg, color: COLORS.redDeep }
            : { bg: COLORS.amberBg, color: COLORS.amber };

    const flags = risk.flags || [];

    return (
        <View style={s.container}>
            <View style={s.header}>
                <Text style={s.title}>RISK ASSESSMENT</Text>
                <View style={[s.badge, { backgroundColor: badgeStyle.bg }]}>
                    <Text style={[s.badgeText, { color: badgeStyle.color }]}>{level} Risk</Text>
                </View>
            </View>
            {flags.length > 0 ? flags.map((f, i) => (
                <View key={i} style={s.flag}>
                    <Text style={s.flagIcon}>🔴</Text>
                    <View style={{ flex: 1 }}>
                        <Text style={s.flagText}>{f.flag}</Text>
                        {f.detail && <Text style={s.flagDetail}>{f.detail}</Text>}
                    </View>
                </View>
            )) : (
                <Text style={s.none}>No significant risk factors identified.</Text>
            )}
        </View>
    );
}

const s = StyleSheet.create({
    container: {
        backgroundColor: COLORS.surface,
        borderRadius: BASE.radiusLg,
        padding: 20,
        marginBottom: 16,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    header: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 16 },
    title: { fontSize: 10, fontWeight: '600', color: COLORS.textTertiary, letterSpacing: 1.5 },
    badge: { paddingHorizontal: 12, paddingVertical: 3, borderRadius: 100 },
    badgeText: { fontSize: 11, fontWeight: '600' },
    flag: { flexDirection: 'row', gap: 10, padding: 10, backgroundColor: COLORS.bg, borderRadius: BASE.radiusSm, marginBottom: 8, alignItems: 'flex-start' },
    flagIcon: { fontSize: 12, marginTop: 2 },
    flagText: { fontSize: 13, fontWeight: '500', color: COLORS.textPrimary },
    flagDetail: { fontSize: 11, color: COLORS.textSecondary, marginTop: 2 },
    none: { fontSize: 13, color: COLORS.textSecondary, fontStyle: 'italic' },
});
