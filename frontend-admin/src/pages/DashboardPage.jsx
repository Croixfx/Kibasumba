import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';

import AncTable from '../components/AncTable.jsx';
import SearchRegister from '../components/SearchRegister.jsx';
import SectionA from '../components/SectionA.jsx';
import SectionC from '../components/SectionC.jsx';
import TopBar from '../components/TopBar.jsx';
import { api, errorMessage } from '../lib/api.js';

export default function DashboardPage() {
  const { phone: phoneParam } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState(null);

  // Deep link: /patient/:phone loads that woman's record directly.
  useEffect(() => {
    if (!phoneParam) return;
    let cancelled = false;
    api
      .get('/api/pregnancy/midwife/woman-record/', {
        params: { phone: phoneParam },
      })
      .then((res) => {
        if (!cancelled) setRecord(res.data);
      })
      .catch((err) => toast.error(errorMessage(err)));
    return () => {
      cancelled = true;
    };
  }, [phoneParam]);

  function handleRecordLoaded(data) {
    setRecord(data);
    navigate(`/patient/${data.woman.phone_number}`, { replace: true });
  }

  function handlePregnancySaved(pregnancy) {
    setRecord((r) => ({ ...r, pregnancy }));
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-gray-100">
      <TopBar />
      <main className="mx-auto max-w-4xl min-w-0 space-y-6 p-4 md:p-8">
        <SearchRegister
          initialPhone={phoneParam ?? ''}
          onRecordLoaded={handleRecordLoaded}
        />

        {record === null ? (
          <div className="flex min-h-40 items-center justify-center rounded-2xl border-2 border-dashed border-gray-300 p-8 text-center text-gray-400">
            Shakisha umubyeyi kugira ngo urebe dosiye ye.
          </div>
        ) : (
          <>
            <div className="rounded-2xl bg-white px-6 py-4 shadow">
              <p className="text-xl font-bold text-gray-800">
                {record.pregnancy?.full_name ||
                  record.woman.full_name ||
                  record.woman.phone_number}
              </p>
              <p className="text-sm text-gray-500">
                {record.woman.phone_number}
              </p>
            </div>
            <SectionA
              key={record.woman.phone_number}
              woman={record.woman}
              pregnancy={record.pregnancy}
              onSaved={handlePregnancySaved}
            />
            <AncTable
              key={`anc-${record.woman.phone_number}`}
              woman={record.woman}
              hasPregnancy={record.pregnancy !== null}
              visits={record.anc_visits}
            />
            <SectionC />
          </>
        )}
      </main>
    </div>
  );
}
