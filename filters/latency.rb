class Percentile
  attr_reader :key, :value, :k, :is_calculated

  def initialize(quantile, sample_size)
    # save 50th quantile as "delay_median" field 
    @key = quantile == 50 ? "delay_median" : "delay_#{quantile}th_percentile"
    @k = (quantile / 100.0) * sample_size
    @value = nil
    @is_calculated = false
  end

  def findvalue(curr_count, hist_value)
    if !@is_calculated && curr_count >= @k
      @value = hist_value
      @is_calculated = true
    end
  end
end

def filter(event)
  unsorted_owds = event['result']['histogram-latency']
  owds = Hash[unsorted_owds.sort]
  c = 0
  sum = 0
  owds.each do |key, value|
    kv = key.to_f
    c += value
    sum += kv * value
  end

  if c > 0
    mean = sum / c
    variance = 0
    owds.each do |key, value|
      variance += value * (key.to_f - mean) ** 2
    end
    # adding variance and standard deviation
    variance /= c
    stddev = Math.sqrt(variance)

    # adding the calulation of quantiles
    quantiles = [25, 50, 75, 95]
    percentiles = quantiles.map { |q| Percentile.new(q, c) }
    percentile = percentiles.shift
    curr_count = 0
    owds.sort.each do |key, value|
      hist_value = key.to_f
      curr_count += value
      # percentiles
      while percentile && curr_count >= percentile.k
        percentile.findvalue(curr_count, hist_value)
        if percentile.is_calculated
            # saving quantiles
          event.set(percentile.key, percentile.value)
          percentile = percentiles.shift
        else
          break
        end
      end
    end

  else
    mean = 0
    stddev = 0
    variance = 0
  end
  # saving other statistics
  event.set('delay_mean', mean)
  event.set('delay_sd', stddev)
  event.set('delay_variance', variance)
  return event
end
