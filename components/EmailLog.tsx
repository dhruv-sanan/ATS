import React from "react";
import { EmailDraftInfo } from "@/hooks/useCrewJob";

// This component will receive props to update events.
type EventLogProps = {
  email: string[];
};

export const EmailLog: React.FC<EventLogProps> = ({ email }) => {
  return (
    <div className="flex flex-col h-full">
      <h2 className="text-lg font-semibold mb-2">Event Details</h2>
      <div className="flex-grow overflow-auto border-2 border-gray-300 p-2">
        {email !== undefined && email.length === 0 ? (
          <p>No events yet.</p>
        ) : (
            <div className="p-2 border-b border-gray-200">
              <p>
                {email}
              </p>
            </div>
          )
        }
      </div>
    </div>
  );
};
