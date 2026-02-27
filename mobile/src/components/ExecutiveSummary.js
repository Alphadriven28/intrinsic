import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, BASE } from '../theme';

export default function ExecutiveSummary({ summary }) {
    if (!summary) return null;

    const sections = [
        { key: 'valuation_verdict', heading: 'Valuation Verdict' },
        { key: 'growth_outlook', heading: 'Growth Outlook' },
        { key: 'financial_strength', heading: 'Financial Strength' },
        { key: 'risk_assessment', heading: 'Risk Assessment' },
        { key: 'investment_attractiveness', heading: 'Investment Attractiveness' },
    ];

    return (
        <View style={s.container}>
            <Text style={s.title}>EXECUTIVE SUMMARY</Text>
            {sections.map(({ key, heading }) => {
                const text = summary[key];
                if (!text) return null;
                return (
                    <View key={key} style={s.item}>
                        <Text style={s.heading}>{heading}</Text>
                        <Text style={s.text}>{text}</Text>
                    </View>
                );
            })}
        </View>
    );
}

const s = StyleSheet.create({
    container: {
        backgroundColor: COLORS.surface,
        borderRadius: BASE.radiusLg,
        padding: 24,
        marginBottom: 24,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    title: {
        fontSize: 10, fontWeight: '600', color: COLORS.textTertiary,
        letterSpacing: 1.5, marginBottom: 20, paddingBottom: 10,
        borderBottomWidth: 1, borderBottomColor: COLORS.borderLight,
    },
    item: { marginBottom: 20 },
    heading: { fontSize: 14, fontWeight: '600', color: COLORS.textPrimary, marginBottom: 6 },
    text: { fontSize: 13, color: COLORS.textSecondary, lineHeight: 20 },
});
