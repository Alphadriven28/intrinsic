import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, BASE } from '../theme';

export default function WeightChart({ weighting }) {
    if (!weighting || weighting.error || !weighting.contributions) return null;

    const contributions = Object.values(weighting.contributions).sort((a, b) => b.weight - a.weight);
    if (contributions.length === 0) return null;

    const maxWeight = Math.max(...contributions.map(c => c.weight));
    const fmt = (v) => v != null ? `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—';

    return (
        <View style={s.container}>
            <Text style={s.sectionTitle}>MODEL WEIGHT DISTRIBUTION</Text>
            {contributions.map((c) => (
                <View key={c.name} style={s.row}>
                    <View style={s.rowHeader}>
                        <Text style={s.rowName}>{c.name}</Text>
                        <Text style={s.rowPct}>{c.weight}%</Text>
                    </View>
                    <View style={s.barWrap}>
                        <View style={[s.bar, { width: `${(c.weight / maxWeight) * 100}%` }]} />
                    </View>
                    <View style={s.rowDetail}>
                        <Text style={s.rowIV}>{fmt(c.value)}</Text>
                        <Text style={s.rowContrib}>→ {fmt(c.contribution)}</Text>
                    </View>
                </View>
            ))}
            <View style={s.total}>
                <Text style={s.totalLabel}>WEIGHTED INTRINSIC VALUE</Text>
                <Text style={s.totalValue}>{fmt(weighting.weighted_intrinsic_value)}</Text>
            </View>
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
    sectionTitle: { fontSize: 10, fontWeight: '600', color: COLORS.textTertiary, letterSpacing: 1.5, marginBottom: 16 },
    row: { marginBottom: 14 },
    rowHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
    rowName: { fontSize: 13, fontWeight: '600', color: COLORS.textPrimary },
    rowPct: { fontSize: 13, fontWeight: '600', color: COLORS.blue },
    barWrap: { height: 6, backgroundColor: COLORS.borderLight, borderRadius: 3, overflow: 'hidden', marginBottom: 4 },
    bar: { height: '100%', borderRadius: 3, backgroundColor: COLORS.blue },
    rowDetail: { flexDirection: 'row', gap: 10 },
    rowIV: { fontSize: 11, fontWeight: '500', color: COLORS.textSecondary },
    rowContrib: { fontSize: 11, color: COLORS.textTertiary },
    total: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: 16,
        marginTop: 8,
        borderTopWidth: 2,
        borderTopColor: COLORS.textPrimary,
    },
    totalLabel: { fontSize: 11, fontWeight: '600', letterSpacing: 0.6, color: COLORS.textPrimary },
    totalValue: { fontSize: 20, fontWeight: '700', color: COLORS.textPrimary },
});
