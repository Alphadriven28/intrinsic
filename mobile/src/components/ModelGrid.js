import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, BASE } from '../theme';

const MODEL_META = {
    dcf: { name: 'DCF', desc: 'Discounted Cash Flow' },
    relative: { name: 'Relative', desc: 'P/E, P/B, EV/EBITDA' },
    ddm: { name: 'DDM', desc: 'Dividend Discount' },
    residual_income: { name: 'Residual Income', desc: 'Excess Return' },
    asset_based: { name: 'Asset-Based', desc: 'Net Asset Value' },
    epv: { name: 'EPV', desc: 'Earnings Power' },
    graham: { name: 'Graham', desc: 'Graham Formula' },
    sotp: { name: 'SOTP', desc: 'Sum of Parts' },
    eva: { name: 'EVA', desc: 'Economic Value Added' },
};

export default function ModelGrid({ models, weighting, currentPrice }) {
    if (!models) return null;

    const weights = weighting?.weights || {};
    const fmt = (v) => v != null ? `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—';

    const entries = Object.entries(models)
        .filter(([, m]) => m.value && m.value > 0 && !m.error)
        .sort((a, b) => (weights[b[0]] || 0) - (weights[a[0]] || 0));

    const errorModels = Object.entries(models)
        .filter(([, m]) => m.error || !m.value || m.value <= 0);

    return (
        <View style={s.section}>
            <Text style={s.sectionTitle}>9-MODEL VALUATION GRID</Text>
            <View style={s.grid}>
                {entries.map(([key, model]) => {
                    const meta = MODEL_META[key] || { name: key, desc: '' };
                    const weight = weights[key];
                    const upside = currentPrice > 0 ? ((model.value - currentPrice) / currentPrice * 100) : 0;
                    const isUnder = upside >= 0;

                    return (
                        <View key={key} style={[s.tile, { borderTopColor: isUnder ? COLORS.green : COLORS.red }]}>
                            <View style={s.tileHeader}>
                                <Text style={s.tileName}>{meta.name}</Text>
                                {weight != null && (
                                    <View style={s.weightBadge}><Text style={s.weightText}>{weight}%</Text></View>
                                )}
                            </View>
                            <Text style={s.tileDesc}>{meta.desc}</Text>
                            <Text style={s.tileValue}>{fmt(model.value)}</Text>
                            <Text style={[s.tileUpside, { color: isUnder ? COLORS.greenDeep : COLORS.redDeep }]}>
                                {isUnder ? '+' : ''}{upside.toFixed(1)}%
                            </Text>
                        </View>
                    );
                })}
            </View>
            {errorModels.length > 0 && (
                <View style={s.excluded}>
                    <Text style={s.excludedText}>
                        <Text style={{ fontWeight: '600' }}>Excluded: </Text>
                        {errorModels.map(([key, m]) => `${MODEL_META[key]?.name || key} (${m.error || 'N/A'})`).join(' · ')}
                    </Text>
                </View>
            )}
        </View>
    );
}

const s = StyleSheet.create({
    section: { marginBottom: 16 },
    sectionTitle: { fontSize: 10, fontWeight: '600', color: COLORS.textTertiary, letterSpacing: 1.5, marginBottom: 12 },
    grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
    tile: {
        backgroundColor: COLORS.surface,
        borderRadius: BASE.radiusMd,
        padding: 16,
        borderWidth: 1,
        borderColor: COLORS.border,
        borderTopWidth: 3,
        width: '48%',
        flexGrow: 1,
    },
    tileHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 },
    tileName: { fontSize: 13, fontWeight: '600', color: COLORS.textPrimary },
    weightBadge: { backgroundColor: COLORS.blueBg, paddingHorizontal: 8, paddingVertical: 1, borderRadius: 100 },
    weightText: { fontSize: 10, fontWeight: '600', color: COLORS.blue },
    tileDesc: { fontSize: 10, color: COLORS.textTertiary, marginBottom: 8 },
    tileValue: { fontSize: 18, fontWeight: '700', color: COLORS.textPrimary, marginBottom: 2 },
    tileUpside: { fontSize: 13, fontWeight: '600' },
    excluded: { backgroundColor: COLORS.borderLight, borderRadius: BASE.radiusSm, padding: 10, marginTop: 10 },
    excludedText: { fontSize: 11, color: COLORS.textTertiary },
});
