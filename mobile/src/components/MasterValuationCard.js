import React from 'react';
import { View, Text, StyleSheet, LinearGradient } from 'react-native';
import { COLORS, BASE } from '../theme';

const RATING_COLORS = {
    'Strong Buy': { bg: 'rgba(52,199,89,0.2)', text: '#4ADE80' },
    'Buy': { bg: 'rgba(52,199,89,0.15)', text: '#86EFAC' },
    'Hold': { bg: 'rgba(255,149,0,0.15)', text: '#FCD34D' },
    'Weak': { bg: 'rgba(255,59,48,0.12)', text: '#FCA5A5' },
    'Avoid': { bg: 'rgba(255,59,48,0.2)', text: '#F87171' },
};

export default function MasterValuationCard({ valuation, weighting, master }) {
    if (!valuation || valuation.error) {
        return (
            <View style={s.container}>
                <Text style={s.title}>VALUATION INTELLIGENCE</Text>
                <Text style={s.empty}>Valuation data unavailable</Text>
            </View>
        );
    }

    const weightedIV = weighting?.weighted_intrinsic_value;
    const currentPrice = valuation.current_price;
    const displayIV = weightedIV && weightedIV > 0 ? weightedIV : valuation.intrinsic_value;
    const upside = currentPrice > 0 ? ((displayIV - currentPrice) / currentPrice * 100) : 0;
    const mos = displayIV > 0 ? ((displayIV - currentPrice) / displayIV * 100) : 0;
    const rating = master?.rating || 'Hold';
    const ratingStyle = RATING_COLORS[rating] || RATING_COLORS['Hold'];

    const fmt = (v) => v != null ? `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—';

    return (
        <View style={s.container}>
            <View style={s.header}>
                <View>
                    <Text style={s.title}>VALUATION INTELLIGENCE</Text>
                    <View style={s.meta}>
                        {weighting?.company_type_label && (
                            <View style={s.typeBadge}><Text style={s.typeBadgeText}>{weighting.company_type_label}</Text></View>
                        )}
                        <Text style={s.modelCount}>{valuation.model_count || 0} models</Text>
                    </View>
                </View>
                <View style={[s.ratingBadge, { backgroundColor: ratingStyle.bg }]}>
                    <Text style={s.ratingLabel}>RATING</Text>
                    <Text style={[s.ratingValue, { color: ratingStyle.text }]}>{rating}</Text>
                    {master?.investment_score != null && (
                        <Text style={[s.ratingScore, { color: ratingStyle.text }]}>{master.investment_score}/100</Text>
                    )}
                </View>
            </View>

            <View style={s.values}>
                <ValueBlock label="Current Price" value={fmt(currentPrice)} />
                <Text style={s.arrow}>→</Text>
                <ValueBlock label="Weighted IV" value={fmt(displayIV)} highlight={upside >= 0 ? COLORS.green : COLORS.red} />
                <ValueBlock label="Upside / Downside" value={`${upside >= 0 ? '+' : ''}${upside.toFixed(1)}%`} highlight={upside >= 0 ? COLORS.green : COLORS.red} />
                <ValueBlock label="Margin of Safety" value={`${mos >= 0 ? '+' : ''}${mos.toFixed(1)}%`} highlight={mos >= 0 ? COLORS.green : COLORS.red} />
            </View>
        </View>
    );
}

function ValueBlock({ label, value, highlight }) {
    return (
        <View style={s.valueBlock}>
            <Text style={s.valueLabel}>{label}</Text>
            <Text style={[s.valueText, highlight && { color: highlight }]}>{value}</Text>
        </View>
    );
}

const s = StyleSheet.create({
    container: {
        backgroundColor: COLORS.heroStart,
        borderRadius: BASE.radiusXl,
        padding: 24,
        marginBottom: 16,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 24,
    },
    title: { fontSize: 10, fontWeight: '600', color: 'rgba(255,255,255,0.5)', letterSpacing: 2 },
    meta: { flexDirection: 'row', gap: 8, marginTop: 6 },
    typeBadge: { backgroundColor: 'rgba(255,255,255,0.1)', paddingHorizontal: 10, paddingVertical: 2, borderRadius: 100 },
    typeBadgeText: { fontSize: 11, color: 'rgba(255,255,255,0.7)', fontWeight: '500' },
    modelCount: { fontSize: 11, color: 'rgba(255,255,255,0.4)', paddingVertical: 2 },
    empty: { textAlign: 'center', color: 'rgba(255,255,255,0.5)', paddingVertical: 24 },
    ratingBadge: { alignItems: 'center', paddingHorizontal: 20, paddingVertical: 12, borderRadius: BASE.radiusMd, minWidth: 100 },
    ratingLabel: { fontSize: 9, letterSpacing: 1, opacity: 0.6, color: '#fff', marginBottom: 2 },
    ratingValue: { fontSize: 17, fontWeight: '700' },
    ratingScore: { fontSize: 11, marginTop: 2, opacity: 0.7 },
    values: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: 16 },
    valueBlock: { gap: 2 },
    valueLabel: { fontSize: 9, textTransform: 'uppercase', letterSpacing: 0.8, color: 'rgba(255,255,255,0.45)', fontWeight: '500' },
    valueText: { fontSize: 22, fontWeight: '700', color: '#FFFFFF' },
    arrow: { fontSize: 18, color: 'rgba(255,255,255,0.2)' },
});
