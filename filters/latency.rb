def filter(event)
    owds = event.get('[result][histogram-latency]')
    c = 0
    sum = 0
    owds.each do |key, value|
        c=c+value
        sum=sum+key.to_f*value
    end
    event.set('owd',sum/c)
    # puts c, sum, sum/c
    return [event]
end