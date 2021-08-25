import React from 'react';
import { useDispatch } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { Typography, Button } from 'antd';
import { plannerActions } from '../../../actions/plannerActions';
import './steps.less';

const { Title } = Typography;
export const DetailStep = () => {
    const dispatch = useDispatch();
    const history = useHistory();
    const currYear = parseInt(new Date().getFullYear());
    const [yearStart, setYearStart] = React.useState(currYear);
    const [yearStartError, setYearStartError] = React.useState(false);
    // Adjust this when be is linked
    const [yearEnd, setYearEnd] = React.useState(currYear + 3);
    const [yearEndError, setYearEndError] = React.useState(false);

    const [outOfDateError, setOutOfDateError] = React.useState(false);
    const handleStartYear = (e) => {
        const input = parseInt(e.target.value);
        setYearStart(input);
        // Our website may be out of date for the user
        setOutOfDateError(input < currYear - 10);

        // Starting year cannot be after ending year
        setYearStartError(input >= yearEnd);

        (outOfDateError || yearStartError) 
        ? e.target.classlist.add('steps-input-warning') 
        : e.target.classlist.remove('steps-input-warning');
    }

    const handleEndYear = (e) => {
        const input = parseInt(e.target.value);
        setYearEnd(input);
        
        // Our website may be out of date for the user
        setOutOfDateError(input > currYear + 10)
        
        // Ending year cannot be before starting year
        setYearEndError(input <= yearStart);
        
        (outOfDateError || yearEndError) 
        ? e.target.classlist.add('steps-input-warning') 
        : e.target.classlist.remove('steps-input-warning');

    }
    return (
        <div className='steps-root-container'>
            <Title level={3} className='text'>
                I start in
            </Title>
            <input 
                className='steps-search-input'
                type='number'
                value={yearStart}
                onChange={(e) => handleStartYear(e)}
            />
            <Title level={3} className='text'>
                and complete my degree in
            </Title>
            <input 
                className='steps-search-input'
                type='number'
                value={yearEnd}
                onChange={(e) => handleEndYear(e)}
            />

            {(!yearStartError && !yearEndError ) && (
                <Button
                    className='steps-next-btn'
                    type="primary"
                    onClick={() => {
                        const degreeLength = yearEnd - yearStart;
                        dispatch(plannerActions('SET_YEAR_START', yearStart));
                        dispatch(plannerActions('SET_DEGREE_LENGTH', degreeLength))
                        history.push('/course-selector');
                }}>
                    Start browsing courses
                </Button>
            )}
        </div>
    )
}