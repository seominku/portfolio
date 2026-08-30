import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '\uad6c\ubbfc\uc11c | Portfolio',
  description: '\uad6c\ubbfc\uc11c\uc758 \ub300\ud68c \ucc38\uac00 \ubc0f \uac8c\uc784 \uac1c\ubc1c \ud504\ub85c\uc81d\ud2b8 \ubc1c\ud45c \ud3ec\ud2b8\ud3f4\ub9ac\uc624',
  openGraph: {
    title: '\uad6c\ubbfc\uc11c \ud3ec\ud2b8\ud3f4\ub9ac\uc624',
    description: '\ub300\ud68c \u00b7 \uac8c\uc784 \u00b7 \uac1c\ubc1c \ub3c4\uad6c',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '\uad6c\ubbfc\uc11c \ud3ec\ud2b8\ud3f4\ub9ac\uc624',
    description: '\ub300\ud68c \u00b7 \uac8c\uc784 \u00b7 \uac1c\ubc1c \ub3c4\uad6c',
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
