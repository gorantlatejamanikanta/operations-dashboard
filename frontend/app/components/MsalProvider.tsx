"use client";

import { MsalProvider as MsalProviderBase } from "@azure/msal-react";
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from "@/app/lib/msalConfig";
import { useState, useEffect } from "react";

const msalInstance = typeof window !== "undefined" 
  ? new PublicClientApplication(msalConfig)
  : null;

export function MsalProvider({ children }: { children: React.ReactNode }) {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (msalInstance) {
      msalInstance.initialize().then(() => {
        setIsReady(true);
      });
    } else {
      setIsReady(true);
    }
  }, []);

  if (!isReady || !msalInstance) {
    return <>{children}</>;
  }

  return (
    <MsalProviderBase instance={msalInstance}>
      {children}
    </MsalProviderBase>
  );
}
