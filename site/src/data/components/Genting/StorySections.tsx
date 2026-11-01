'use client';

import { AheadSection } from '@/data/components/Genting/sections/Ahead';
import { CashCallSection } from '@/data/components/Genting/sections/CashCall';
import { CompanySection } from '@/data/components/Genting/sections/Company';
import { DebtSection } from '@/data/components/Genting/sections/Debt';
import { MethodSection } from '@/data/components/Genting/sections/Method';
import { NewYorkSection } from '@/data/components/Genting/sections/NewYork';
import { OfferSection } from '@/data/components/Genting/sections/Offer';

export function StorySections() {
  return (
    <>
      <OfferSection />
      <NewYorkSection />
      <DebtSection />
      <CashCallSection />
      <CompanySection />
      <AheadSection />
      <MethodSection />
    </>
  );
}
