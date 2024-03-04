import React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import { CardContent, CardHeader, List, ListItem, Typography } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';

import TrackCard from './TrackCard';

import {getResultsData} from './utilities'

const ResultsScroll = ({closeFunc, shareFunc}) => {
  return <Card sx={{
      borderRadius: 5,
      backgroundColor: '#FFFDDD',
      height: {
        xs: "90vh",
        md: "82vh",
      },
      width: {
        xs: "90vw",
        md: "85vw",
      },
      minHeight: '1000',
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)'
  }}>
    <CardHeader sx={{height: '5vh', p: 0, pt: 2, transform: 'translate(15px, 0)'}}
      title='Thanks for playing!'
      titleTypographyProps={
        {
          fontSize: {
            xs: "max(20px, 1vh)",
            sm: "max(20px, 1vh)",
            md: "max(20px, 2vh)",
            lg: "max(20px, 2vh)",
            xl: "max(20px, 3vh)",
          },
          align: 'center',
          whiteSpace: 'nowrap'
        }
      }
      subheader='Here are your results:'
      subheaderTypographyProps={
        {
          fontSize: "max(15px, 2vh)",
          align: 'center'
        }
      }
      action={
        <IconButton onClick={closeFunc} sx={{transform: 'translate(-28px, 0)'}}>
          <CloseIcon/>
        </IconButton>
      }
    />
    <CardContent sx={{p: 0}}>
      <Grid container sx={{py: 2}} direction="column" justifyContent="space-around" wrap="nowrap">
        <Grid item xs={10}>
          <Box sx={{border: 1, mx: {xs: 2, md: 3}, p: 0, height: {xs: "70vh", md: "66vh"}, overflow: 'auto'}}>
            <List disablePadding>
              {aBunchOfListItems()}
            </List>
          </Box>
        </Grid>
        <Grid item xs={1} alignSelf="center">
          <Box sx={{p: 1}}>
            <Button size="small" variant="contained" onClick={shareFunc}>
              Share Results
            </Button>
          </Box>
        </Grid>
      </Grid>
    </CardContent>
  </Card>;
}

const playcountFormatter = (numPlays) => {
  if (numPlays < 10000) {
    return `${numPlays}\nListens`;
  }
  else if (numPlays < 1000000) {
    return `${Math.round(numPlays/100)/10}K\nListens`;
  }
  else if (numPlays < 1000000000) {
    return `${Math.round(numPlays/100000)/10}M\nListens`;
  }
  else if (numPlays < 1000000000000) {
    return `${Math.round(numPlays/100000000)/10}B\nListens`;
  }
}

const Result = ({date, selection, track1Id, track1Playcount, track2Id, track2Playcount, finalized}) => {
  return <Grid container sx={{
      height: {
        xs: 340,
        md: 160,
      },
    }} columns={30} justifyContent='space-between' alignItems='center'>
      <Grid item xs={30} md={1} justifyItems='center'>
        <Grid container alignItems='center' justifyContent='space-around' direction='column'>
          <Grid item>
            <Card sx={{
              backgroundColor: 'lightblue',
              width: {
                xs: 160,
                md: 140,
              },
              transform: {
                xs: 'translate(0, 4px)',
                md: 'rotate(270deg) translate(0, -42px)',
              },
              }}>
                <Typography variant='h6' align='center'>
                  {date}
                </Typography>
            </Card>
          </Grid>
        </Grid>
      </Grid>
      <Grid item xs={30} md={29}>
        <Grid container sx={{
          height: {
            xs: 290,
            md: 160,
          }
          }} columns={40} justifyContent='space-around' alignItems='center'>
          <Grid item xs={38} md={18}>
            <TrackCard
              forceSmall
              trackId={track1Id}
              numListens={playcountFormatter(track1Playcount)}
              isEnabled={false}
              isSelected={selection==='1'}
              isCorrect={selection==='1' && track1Playcount >= track2Playcount}
            />
          </Grid>
          <Grid item xs={38} md={18}>
            <TrackCard
              forceSmall
              trackId={track2Id}
              numListens={playcountFormatter(track2Playcount)}
              isEnabled={false}
              isSelected={selection==='2'}
              isCorrect={selection==='2' && track1Playcount <= track2Playcount}
            />
          </Grid>
        </Grid>
      </Grid>
  </Grid>
}

const aBunchOfListItems = () => {
  // display a week's worth of data here
  let tracks = getResultsData();
  tracks = tracks.slice(0, Math.min(tracks.length, 7));

  let items = [];
  for (let i = 0; i < tracks.length; i++) {
    items.push(
      <ListItem disablePadding key={tracks[i]['dateStr']} sx={{borderBottom: i===(tracks.length-1) ? 0 : 1}}>
        <Result
          date={tracks[i]['dateStr']}
          selection={tracks[i]['selection']}
          track1Id={tracks[i]['track1Id']}
          track1Playcount={parseInt(tracks[i]['track1Playcount'])}
          track2Id={tracks[i]['track2Id']}
          track2Playcount={parseInt(tracks[i]['track2Playcount'])}
        />
      </ListItem>
    )
  }
  return items;
}

export default ResultsScroll;
