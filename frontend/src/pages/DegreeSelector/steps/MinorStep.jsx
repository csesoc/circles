import React from 'react';
import { Button, Typography } from 'antd';
import { degreeActions } from '../../../actions/degreeActions';
import { useDispatch } from 'react-redux'
import './steps.less';
const options = [
    'MINOR 1', 
    'MINOR 2', 
    'MINOR 3', 
    'MINOR 4', 
    'No minors',
];  
const { Title } = Typography;
export const MinorStep = () => {
    const dispatch = useDispatch();
    // const program = useSelector(store => store.degree.program);
    // Fetch the minors
    const [selected, setSelected] = React.useState("Select Minor"); 
    return (
        <div className="steps-root-container">
             <Title level={3} className="text">
                and minoring in (optional)
            </Title>
            <select 
                className='steps-dropdown'
                name="Select Minor"
                onChange={value => setSelected(value)} 
            >
                <option
                    key={0}
                    value={"Select Minor"}
                >
                    Select Minor
                </option>
                {options.map((option, index) =>
                    <option
                        key={index}
                        value={option}
                    >
                        {option}
                    </option>
                )}
            </select>

            <Button type="primary" className='steps-next-btn'
                onClick={() => {
                    dispatch(degreeActions('SET_MINOR', selected));
                    dispatch(degreeActions('NEXT_STEP'))
                }}
            >
                Next
            </Button>
            
        </div>
        
       
    )

}