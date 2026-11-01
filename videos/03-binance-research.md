# Binance hack: research file (as of Nov 1, 2026)

Compiled from web-search summaries only. I could not open the articles, so **read the primary sources yourself before scripting.** Tags: **[Solid]** = reported by several major outlets; **[Reported]** = one or two sources or analyst claims; **[Disputed]** = sources disagree; **[Unknown]** = not yet public.

Framing note: Binance is the **victim** of a theft here. Do not call it a "Binance scam." Say "hack," "heist" or "theft."

## What happened

- **[Solid]** Oct 29, 2026: attackers drained Binance hot wallets. Binance's own estimate is about **$6.3 billion** in total impact, with about **$3 billion frozen**. It is described as the largest crypto theft on record. Sources: [CNBC](https://www.cnbc.com/2026/10/29/circle-tether-freeze-funds-impacted-by-potential-binance-security-issue.html), [NBC News](https://www.nbcnews.com/business/markets/binance-hack-tether-circle-stablecoins-rcna606445), [Fox Business](https://www.foxbusiness.com/technology/binance-says-security-incident-had-estimated-6-3b-impact-3b-assets-frozen), [The Hacker News](https://thehackernews.com/2026/10/binance-suffers-security-breach.html), [Bloomberg](https://www.bloomberg.com/news/articles/2026-10-29/binance-founder-says-possible-hack-of-exchange-bitcoin-falls).
- **[Solid]** Previous record: Bybit, about $1.4-1.5B, Feb 2025, attributed by the FBI to North Korea's TraderTraitor. Source: [Quartz](https://qz.com/major-crypto-hacks-history), [CryptoTimes](https://www.cryptotimes.io/insights/biggest-crypto-hacks/).
- **[Reported]** Binance's CEO-level founder CZ posted on X the evening it happened: "User funds are safe! It does look like a hack on Binance." Source: [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/binance-major-shareholder-says-user-005223673.html).
- **[Solid]** Binance suspended deposits and withdrawals and pledged to cover all losses. Sources: [InvestingLive](https://investinglive.com/cryptocurrency/binance-halts-deposits-and-withdrawals-pledges-to-cover-all-losses-from-suspected-hack/), [Fox Business](https://www.foxbusiness.com/technology/binance-says-security-incident-had-estimated-6-3b-impact-3b-assets-frozen).

## How it worked (preliminary; Binance's full post-mortem is **[Unknown]**, not yet published)

- **[Reported]** Binance's early finding: the break-in "may involve a compromised DevOps engineer's laptop," from which the attacker reached a service container and submitted unauthorized withdrawals. Binance said it found no evidence that wallet private keys leaked. Source: [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/binance-says-compromised-engineer-laptop-161203953.html).
- **[Reported]** Binance's co-CEO Richard Teng later said it was a more complex process than misuse of one engineer's permissions, and investigators found additional breach points. Source: [Euronews](https://www.euronews.com/2026/10/30/how-the-binance-hack-happened-and-who-was-behind-it).
- **[Reported]** TRM Labs says the hot-wallet signing system was likely compromised and notes the early staging resembles the Bybit heist. Source: [TRM Labs](https://www.trmlabs.com/resources/blog/north-korea-steals-usd-6-36-billion-from-binance-in-the-largest-hack-in-history).
- **[Disputed]** Technical details from lower-reliability blogs (a "sweeper contract," 50 signatures, EIP-7702, Tornado Cash staging, exact UTC times such as first outflow ~20:04) are not confirmed by Binance or major outlets. Use only if the post-mortem confirms them.

## Who is blamed

- **[Reported]** TRM Labs: North Korea's **TraderTraitor** group, "high confidence." Chainalysis: likely TraderTraitor, citing stolen Binance funds mixing with proceeds from last month's Bitget theft, which was already attributed to North Korea. Sources: [Chainalysis](https://www.chainalysis.com/blog/binance-exploit-latest-findings-and-response/), [Decrypt](https://decrypt.co/382224/trm-and-chainalysis-tie-6-4b-binance-hack-to-north-koreas-tradertraitor), [Cointelegraph](https://cointelegraph.com/news/north-korea-linked-to-63b-binance-hack-by-crypto-investigators).
- **[Reported, verify wording]** NBC News and ABC News headlines say the **FBI** attributed it to North Korea, and the FBI said it is coordinating with the U.S. Attorney's Office for D.C. The Secret Service is also involved. Sources: [NBC News](https://www.nbcnews.com/business/business-news/fbi-says-north-korea-was-6-billion-binance-crypto-hack-rcna606758), [ABC News](https://abcnews.com/Business/binance-estimates-security-breach-impact-63-billion/story?id=137698510), [Decrypt](https://decrypt.co/382268/secret-service-fbi-binance-hack-probe), [Bloomberg](https://www.bloomberg.com/news/articles/2026-10-30/binance-s-6-billion-heist-rattles-crypto-and-draws-fbi-scrutiny). One low-reliability site's headline mentions doubts about the attribution; I did not find that in major outlets.
- Say "the FBI said" only after you read the FBI statement; say "analysts at TRM Labs and Chainalysis say" for the rest.

## Money: frozen, covered, still missing

- **[Solid]** About $3B frozen (Binance's figure). Tether froze more than $1.5B in USDT; Circle froze over $800M in USDC (reported as $823M). Other issuers also froze assets. Sources: [Decrypt](https://decrypt.co/382268/secret-service-fbi-binance-hack-probe), [Tech Report](https://techreport.com/news/software/circle-tether-freeze-binance-hack/), [CBS News](https://www.cbsnews.com/news/binance-crypto-hack-stolen-funds-recovery/).
- **Frozen is not recovered.** CBS reports that freezing is step one; law enforcement then needs a seizure warrant to move funds to a U.S. government account.
- **[Reported]** The attacker reportedly still controls about $3.33B that issuers cannot freeze. Source: [The Hacker News](https://thehackernews.com/2026/10/binance-suffers-security-breach.html).
- **[Reported]** Binance's SAFU emergency fund is roughly $1B ($1.18B per one estimate), far less than the loss, so Binance's own balance sheet covers the rest. Source: [CCN](https://www.ccn.com/education/crypto/binance-6-3b-hack-1b-safu-fund-losses-coverage/).
- **[Reported, unconfirmed]** Binance has covered about 95% of the loss. Source: [BeInCrypto](https://beincrypto.com/binance-restores-withdrawals-after-hack/).
- **[Reported]** Withdrawals began reopening Nov 1, starting with Bitcoin; Solana and XRP were still paused in one report. Sources: [BeInCrypto](https://beincrypto.com/binance-restores-withdrawals-after-hack/), [CryptoTicker](https://cryptoticker.io/en/binance-withdrawals-solana-xrp-paused-after-hack/).
- **[Reported]** Binance said it would publish an updated proof of reserves after the incident is resolved; I found no confirmation it has been published. Binance's co-CEO said $3B is about 2% of total user assets and reserves.

## Market reaction

- **[Solid]** Bitcoin fell about 4% to roughly $77,000 (six-week low about $76,368). BNB fell about 6-8%. Ether fell about 4.4%. Sources: [CNBC](https://www.cnbc.com/2026/10/30/bitcoin-ether-price-binance-security-scare-rattles-crypto-markets.html), [The Block](https://www.theblock.co/news/markets/2026-10-29-bitcoin-slides-below-77000-binance-hack-432183), [Cointelegraph](https://cointelegraph.com/markets/binance-hack-rattles-crypto-markets-bnb-bitcoin-slide).
- **[Reported]** About $1.5B in liquidations; Fear & Greed Index at 30. CNBC noted bitcoin has fallen an average of 8.3% in the first 24 hours after past exchange exploits, so this reaction was milder.
- **[Reported]** Analysts called the spillover "fairly contained," since the attack hit one firm's systems, not the Bitcoin network.

## Disputed numbers (do not state as fact)

| Item | Range in sources |
|---|---|
| Total stolen | $6.15B (BitOK) / $6.3B (Binance) / $6.36B (TRM) / $6.4B (Chainalysis) |
| Frozen | $2.54B / $2.7B / $2.84B / about $3B |
| How long | about 20 minutes to under 4 hours |
| Blockchains | 9, 10 or 11 |
| Binance losses covered | "about 95%" (one source); one report says CZ put losses slightly above $1B, which conflicts and I could not explain |

Use phrases like "Binance estimates about six billion dollars."

## Context: earlier Binance incidents (well sourced)

- **May 7, 2019:** about 7,000 BTC (about $40.7M) via API keys and two-factor codes, covered by SAFU. Sources: [CoinDesk](https://www.coindesk.com/markets/2019/05/07/hackers-steal-407-million-in-bitcoin-from-crypto-exchange-binance), [Forbes](https://www.forbes.com/sites/michaeldelcastillo/2019/05/07/binance-ceo-cz-reports-40-million-bitcoin-hack/).
- **Oct 6, 2022:** attacker forged proofs on the BNB Chain bridge and minted about 2 million BNB (about $570M at the time); chain halted, patched by a hard fork on Oct 12. Sources: [Elliptic](https://www.elliptic.co/blog/analysis/attack-mints-569-million-worth-of-bnb-tokens-in-bsc-bridge-exploit), [CNBC](https://www.cnbc.com/2022/10/07/more-than-100-million-worth-of-binances-bnb-token-stolen-in-another-major-crypto-hack.html).
- **Other record thefts to compare:** Bybit about $1.5B (Feb 2025, TraderTraitor per FBI); Ronin about $540-625M (Mar 2022, North Korea-linked).

## Still unknown (say so in the video)

- Binance's full technical post-mortem
- How the attackers got in beyond the early "laptop" statement
- Whether charges or seizures follow, and how much is ever recovered
- Whether the updated proof of reserves is out and what it shows

## Video angles

1. **"How $6.3 billion disappeared from Binance"**: the story in order (attack, freeze, who is blamed, what's left). About 6-7 minutes. Most searchable, and most competitors will do this.
2. **"The man behind the hack: North Korea's crypto thieves"**: Bybit, Ronin, Bitget, now Binance. A strong original angle if you stick to the FBI and analyst reports.
3. **"Frozen is not recovered"**: why the $3B freeze is not the same as getting money back. A smaller, more distinctive angle that few will cover well.

**My recommendation:** angle 1 with a short angle-2 section (the Bybit comparison is already sourced) and one clear line that frozen is not recovered.

## Title options

1. How $6.3 Billion Disappeared From Binance
2. The Binance Hack: What We Know So Far
3. North Korea vs Binance: The Biggest Crypto Heist Ever

## Rules for the script

- Attribute every claim ("according to Binance," "TRM Labs says," "the FBI said").
- Don't blame the engineer or speculate about an inside job.
- No financial advice and no price predictions.
- Don't copy another creator's video or an article's wording.
- Put the date on screen ("as of Nov 1, 2026") and pin a comment for updates.
