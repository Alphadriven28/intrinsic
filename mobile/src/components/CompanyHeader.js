import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, BASE } from '../theme';

export default function CompanyHeader({ company, valuation, weighting }) {
    if (!company) return null;

    const weightedIV = weighting?.weighted_intrinsic_value;
    const displayIV = weightedIV && weightedIV > 0 ? weightedIV : valuation?.intrinsic_value;
    const mos = displayIV && displayIV > 0 ? ((displayIV - company.price) / displayIV * 100) : null;

    const fmt = (v) => v != null ? `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—';
    const fmtCap = (v) => {
        if (!v) return '—';
        if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
        if (v >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
        return `$${(v / 1e6).toFixed(0)}M`;
    };

    const mosColor = mos > 0 ? COLORS.greenDeep : mos < -20 ? COLORS.redDeep : COLORS.amber;

    return (
        <View style={s.container}>
            <View style={s.top}>
                <Text style={s.name}>{company.name}</Text>
                <Text style={s.ticker}>{company.ticker}</Text>
                {company.exchange && <View style={s.exchangeBadge}><Text style={s.exchangeText}>{company.exchange}</Text></View>}
            </View>

            <View style={s.metrics}>
                <Metric label="Current Price" value={fmt(company.price)} />
                <Metric label="Weighted IV" value={valuation?.error ? '—' : fmt(displayIV)} valueColor={mosColor} />
                <Metric label="Margin of Safety" value={mos != null ? `${mos > 0 ? '+' : ''}${mos.toFixed(1)}%` : '—'} valueColor={mosColor} />
                <Metric label="Market Cap" value={fmtCap(company.market_cap)} />
                <Metric label="Sector" value={company.sector || '—'} small />
                <Metric label="Beta" value={company.beta?.toFixed(2) || '—'} />
            </View>
        </View>
    );
}

function Metric({ label, value, valueColor, small }) {
    return (
        <View style={s.metric}>
            <Text style={s.metricLabel}>{label}</Text>
            <Text style={[s.metricValue, valueColor && { color: valueColor }, small && { fontSize: 15 }]}>{value}</Text>
        </View>
    );
}

const s = StyleSheet.create({
    container: {
        backgroundColor: COLORS.surface,
        borderRadius: BASE.radiusXl,
        padding: 24,
        marginBottom: 16,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    top: {
        flexDirection: 'row',
        alignItems: 'baseline',
        gap: 8,
        marginBottom: 20,
        flexWrap: 'wrap',
    },
    name: { fontSize: 20, fontWeight: '600', color: COLORS.textPrimary },
    ticker: { fontSize: 15, fontWeight: '500', color: COLORS.textTertiary, letterSpacing: 0.5 },
    exchangeBadge: { backgroundColor: COLORS.borderLight, paddingHorizontal: 10, paddingVertical: 2, borderRadius: 100 },
    exchangeText: { fontSize: 11, fontWeight: '500', color: COLORS.textTertiary },
    metrics: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 20,
    },
    metric: { minWidth: 100 },
    metricLabel: { fontSize: 10, fontWeight: '600', color: COLORS.textTertiary, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 },
    metricValue: { fontSize: 20, fontWeight: '600', color: COLORS.textPrimary },
});
