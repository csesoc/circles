import React, { Suspense, useEffect, useState } from 'react';
import { Tooltip as ReactTooltip } from 'react-tooltip'; // TODO: investigate using antd tooltip?
import type { LiquidConfig } from '@ant-design/plots';
import Spinner from 'components/Spinner';
import { darkGrey, lightGrey, lightYellow, purple, yellow } from 'config/constants';
import useSettings from 'hooks/useSettings';

type Props = {
  completedUOC: number;
  totalUOC: number;
};

const Liquid = React.lazy(() =>
  import('@ant-design/plots').then((plot) => ({ default: plot.Liquid }))
);

const LiquidProgressChart = ({ completedUOC, totalUOC }: Props) => {
  const [percent, setPercent] = useState(0);
  const fillValue = Math.min(completedUOC / totalUOC, 1);

  // light mode text color varies
  let textColor = '';
  if (percent < 0.31) {
    textColor = lightYellow;
  } else if (percent < 0.45) {
    textColor = lightGrey;
  } else if (percent < 0.56) {
    textColor = darkGrey;
  } else {
    textColor = 'white';
  }

  // dark mode always has white text
  const { theme } = useSettings();
  if (theme === 'dark') {
    textColor = 'white';
  }

  // TODO: restore to former glory
  // https://ant-design-charts.antgroup.com/options/plots/label/overview
  // https://ant-design-charts.antgroup.com/options/plots/common/style
  // https://ant-design-charts.antgroup.com/examples/statistics/liquid#liquid
  // https://ant-design-charts.antgroup.com/zh/examples/statistics/gauge/#gauge-color
  // title works, cant figure out how to change text size, (look mayb more textContent)
  // also the filling up is too laggy now
  const config: LiquidConfig = {
    percent,
    width: 320,
    height: 320,
    autoFit: false,
    interaction: {
      tooltip: false
    },
    label: false,
    style: {
      textFill: textColor,
      fill: percent > 0.45 ? purple : yellow,
      stroke: percent > 0.45 ? purple : yellow
    }
  };

  // increment percentage from 0 to fillValue
  useEffect(() => {
    let data = 0.0;
    const time = 30;
    const interval = setInterval(() => {
      data += 0.01;
      if (fillValue && data <= fillValue + 0.01) {
        setPercent(data);
      } else {
        clearInterval(interval);
      }
    }, time);
  }, [fillValue]);

  return (
    <>
      <div id="liquidChart">
        <div data-tip>
          <Suspense fallback={<Spinner text="Loading Progress..." />}>
            <Liquid {...config} />
          </Suspense>
        </div>
      </div>
      <ReactTooltip
        noArrow
        anchorSelect="#liquidChart"
        place="bottom"
        variant={theme === 'dark' ? 'light' : 'dark'}
      >
        {completedUOC} / {totalUOC} UOC
      </ReactTooltip>
    </>
  );
};

export default LiquidProgressChart;
